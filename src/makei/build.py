#!/usr/bin/env python3.9

""" The module used to build a project"""
from datetime import datetime
import shutil
import sys
import os
import time
from pathlib import Path
from tempfile import mkstemp
from typing import Any, Dict, List, Optional

from makei.const import TOBI_PATH, MK_PATH, TARGET_TARGETGROUPS_MAPPING
from makei.ibmi_json import IBMiJson
from makei.iproj_json import IProjJson
from makei.rules_mk import RulesMk
from makei.utils import objlib_to_path, \
    run_command, support_color, print_to_stdout, Colors, colored, get_target_patterns_for_makefile, escape_special_chars


class BuildEnv:
    """ The Build Environment used to build or compile a project. """
    # pylint: disable=too-many-instance-attributes

    color_tty: bool
    src_dir: Path
    targets: List[str]
    make_options: Optional[str]
    tobi_path: Path
    tobi_makefile: Path
    build_vars_path: Path
    build_vars_handle: Path
    curlib: str
    pre_usr_libl: str
    post_usr_libl: str
    iproj_json_path: Path
    iproj_json: IProjJson
    ibmi_env_cmds: str

    tmp_files: List[Path] = []

    success_targets: List[str]
    failed_targets: List[str]
    suppress_make_output: bool = False  # Flag to suppress Make's verbose output

    def __init__(self, targets: List[str] = None, make_options: Optional[str] = None,
                 overrides: Dict[str, Any] = None, trace=False):
        overrides = overrides or {}
        self.src_dir = Path.cwd()
        self.targets = [self._escape_special_chars_internal(t) for t in (targets or ["all"])]
        self.make_options = make_options if make_options else ""
        self.tobi_path = Path(
            overrides["tobi_path"]) if "tobi_path" in overrides else TOBI_PATH
        self.tobi_makefile = MK_PATH / 'Makefile'
        self._trace = trace

        if self._trace:
            trace_dir = Path.cwd() / ".makei-trace"
            trace_dir.mkdir(parents=True, exist_ok=True)
            self.trace_dir = trace_dir / datetime.now().strftime("%Y%m%d_%H%M%S")
            self.trace_dir.mkdir()
            path = self.trace_dir / "BUILDVARSMKPATH"
        else:
            self.build_vars_handle, path = mkstemp()
            os.close(self.build_vars_handle)
            self.trace_dir = None

        self.build_vars_path = Path(path)
        self.iproj_json_path = self.src_dir / "iproj.json"
        self.iproj_json = IProjJson.from_file(self.iproj_json_path)
        self.color = support_color()
        self.iasp = self.iproj_json.iasp
        if len(self.iproj_json.set_ibm_i_env_cmd) > 0:
            cmd_list = self.iproj_json.set_ibm_i_env_cmd
            self.ibmi_env_cmds = "\\n".join(cmd_list)
        else:
            self.ibmi_env_cmds = ""

        self.success_targets = []
        self.failed_targets = []
        # Flag to indicate if make should be skipped
        self.skip_make = False

        self._create_build_vars()

    def __del__(self):
        if not self._trace:
            self.build_vars_path.unlink()

    def dump_resolved_makefile(self):
        """Generate a fully resolved Makefile dump without building."""
        if not self._trace:
            return

        resolved_makefile_path = self.trace_dir / "ResolvedMakefile.txt"
        with resolved_makefile_path.open("w", encoding="utf8") as f:

            def write_line(line_bytes: bytes):
                line = line_bytes.decode()
                f.write(line)

            # For trace, we just need the actual command (second element of tuple)
            _, actual_cmd = self.generate_make_cmd()
            cmd = f"{actual_cmd} -r -R -p -q"
            run_command(cmd, stdout_handler=write_line)

    def generate_make_cmd(self):
        """ Returns the make command used to build the project."""
        cmd = f'/QOpenSys/pkgs/bin/make -k BUILDVARSMKPATH="{self.build_vars_path}"' + \
              f' -k TOBI_PATH="{self.tobi_path}" -f "{self.tobi_makefile}"'
        # Add -s flag to suppress Make's verbose "is up to date" messages
        if self.suppress_make_output:
            cmd = f"{cmd} -s"
        if self.make_options:
            cmd = f"{cmd} {self.make_options}"
        # Escape special characters in target names for Make
        escaped_targets = []
        for t in self.targets:
            if 'HASHESCAPE_' in t or 'DOLLARESCAPE_' in t:
                escaped_targets.append(t)
            else:
                escaped = self._escape_special_chars_internal(t)
                escaped_targets.append(escaped)
        # For display: show 'all' if many targets, otherwise show actual targets
        if len(escaped_targets) > 2:
            display_cmd = f"{cmd} all"
        else:
            display_cmd = f"{cmd} {' '.join(escaped_targets)}"
        actual_cmd = f"{cmd} {' '.join(escaped_targets)}"
        return display_cmd, actual_cmd

    @staticmethod
    def _unescape_special_chars(text: str) -> str:
        """Remove escape sequences for # and $ characters."""
        return text.replace('DOLLARESCAPE_', '$').replace('HASHESCAPE_', '#').replace('\\#', '#')

    @staticmethod
    def _escape_special_chars_internal(text: str) -> str:
        """Add escape sequences for # and $ characters."""
        return text.replace('$', 'DOLLARESCAPE_').replace('#', 'HASHESCAPE_')

    @staticmethod
    def _has_special_chars(text: str) -> bool:
        """Check if text contains special characters or their escape sequences."""
        return any(char in text for char in ('$', '#', 'DOLLARESCAPE_', 'HASHESCAPE_', '\\#'))

    def _check_target_needs_rebuild(self, rule, objlib_path: Path) -> bool:
        """Check if target needs rebuild based on timestamp comparison."""
        # Unescape source and target names using helper
        source_str = self._unescape_special_chars(rule.source_file.replace('$(d)/', '', 1))
        target_unescaped = self._unescape_special_chars(rule.target)
        target_path = objlib_path / target_unescaped
        # Determine source path (QSYS for objects, source dir for files)
        source_path = (Path(source_str) if Path(source_str).is_absolute()
                       else rule.containing_dir / source_str if rule.is_source_file
                       else objlib_path / source_str)
        # Handle missing source
        if not source_path.exists():
            return not target_path.exists()
        # Check target exists (retry once for QSYS)
        target_exists = target_path.exists()
        if not target_exists:
            time.sleep(0.1)
            target_exists = target_path.exists()
            if not target_exists:
                return True
        # Compare timestamps using Path.stat() for both
        return source_path.stat().st_mtime > target_path.stat().st_mtime

    def _prepare_timestamp_check(self, rules_mk_paths, real_targets):
        """Prepare for timestamp checking by filtering paths and determining check strategy."""
        filtered_rules_mk_paths = rules_mk_paths
        check_specific_targets = False
        skip_timestamp_check = False
        if not self.targets or self.targets[0] == "all":
            return filtered_rules_mk_paths, check_specific_targets, skip_timestamp_check
        # Check if target is a directory target
        is_dir_target = any(t.startswith(('DIR_', 'dir_')) for t in self.targets)
        if is_dir_target:
            # Extract directory names and filter Rules.mk paths
            target_dirs = [t[4:].upper() for t in self.targets if t.startswith(('DIR_', 'dir_'))]
            filtered_rules_mk_paths = [
                p for p in rules_mk_paths
                for target_dir in target_dirs
                if self._is_path_under_dir(p.parent, target_dir)
            ]
        elif real_targets:
            # real_targets already contains escaped target names (e.g., HASHESCAPE_HELLO1.PGM)
            # Just use them directly
            self.targets = real_targets
            check_specific_targets = True
        else:
            skip_timestamp_check = True
        return filtered_rules_mk_paths, check_specific_targets, skip_timestamp_check

    def _is_path_under_dir(self, path, target_dir):
        """Check if path is under target directory."""
        try:
            path.relative_to(Path(target_dir))
            return True
        except ValueError:
            return False

    def _build_final_target_list(self, all_rules, special_char_files):
        """Build the final list of targets to pass to Make.
        Args:
            all_rules: List of (rule, objlib_path, escaped_target) tuples
            special_char_files: Dict of {target: needs_rebuild} for special char files
        Returns:
            List of targets to build
        """
        targets_to_build = []
        for rule, objlib_path, escaped_target in all_rules:
            # Special char file: only include if needs rebuild
            if escaped_target in special_char_files:
                if special_char_files[escaped_target]:
                    targets_to_build.append(escaped_target)
            # Normal file: always include (Make will check)
            else:
                targets_to_build.append(escaped_target)
        return targets_to_build

    def _collect_rules_mk_paths(self, root: Path) -> List[Path]:
        """Collect Rules.mk paths by following SUBDIRS chains from root.
        Only folders explicitly declared in SUBDIRS are visited — unlisted
        folders (dot-dirs, work-in-progress, etc.) are completely ignored.
        """
        rules_mk = root / "Rules.mk"
        if not rules_mk.exists():
            return []
        with rules_mk.open() as f:
            subdirs = next(
                (
                    line.split("=", 1)[1].split("#")[0].split()
                    for line in f
                    if line.strip().startswith("SUBDIRS")
                ),
                [],
            )
        result = [rules_mk]
        for subdir in subdirs:
            child = root / subdir
            if child.is_dir():
                result.extend(self._collect_rules_mk_paths(child))
        return result

    def _create_build_vars(self):
        target_file_path = self.build_vars_path

        rules_mk_paths = self._collect_rules_mk_paths(Path("."))
        real_targets = []
        # Create Rules.mk.build for each Rules.mk
        for rules_mk_path in rules_mk_paths:
            rules_mk = RulesMk.from_file(rules_mk_path, str(self.src_dir), map(Path, self.iproj_json.include_path))
            rules_mk_src_obj_mapping = rules_mk.src_obj_mapping.copy()
            if self.targets and self.targets[0] != "all":
                for target in self.targets:
                    if target.startswith("dir_") and target not in real_targets:
                        real_targets.append(target)
                    else:
                        # Target is relative path. i.e. QRPGLESRC/TEST.RPGLE
                        if len(Path(target).parts) > 1:
                            tgt_dir = os.path.dirname(target)
                            tgt = os.path.basename(target)
                            # Target exist in the current Rules.mk and target's rule exists
                            if tgt_dir == str(rules_mk.containing_dir) and tgt.upper() in rules_mk_src_obj_mapping:
                                real_targets.extend(rules_mk_src_obj_mapping.pop(tgt.upper()))
                        # Target is a file name - search all Rules.mk files
                        else:
                            tgt = target
                            # Check if target is already escaped (from parse_rules_mk_for_targets)
                            if 'HASHESCAPE_' in tgt or 'DOLLARESCAPE_' in tgt:
                                # Already a resolved target name, use it directly (avoid duplicates)
                                if tgt not in real_targets:
                                    real_targets.append(tgt)
                            else:
                                # First convert \# from command line to # (actual character)
                                # The src_obj_mapping uses the original source filename (with # and $)
                                # So we search using the unescaped, normalized name
                                tgt_normalized = tgt.replace(r'\#', '#').replace(r'\$', '$').upper()
                                # Search in current Rules.mk using the original source name
                                if tgt_normalized in rules_mk_src_obj_mapping:
                                    resolved = rules_mk_src_obj_mapping.pop(tgt_normalized)
                                    # Escape the resolved targets for comparison with escaped_target
                                    real_targets.extend([escape_special_chars(r) for r in resolved])
                                # If not found in mapping but contains special chars, it might be a target name
                                elif '$' in tgt or '#' in tgt:
                                    escaped_tgt = escape_special_chars(tgt)
                                    if escaped_tgt not in real_targets:
                                        real_targets.append(escaped_tgt)
                                elif tgt not in real_targets:
                                    real_targets.append(tgt)
            rules_mk.build_context = self
            rules_mk_build_path = rules_mk_path.parent / ".Rules.mk.build"
            rules_mk_build_path.write_text(str(rules_mk))
            self.tmp_files.append(rules_mk_build_path)
            # Copy to trace directory
            if self._trace:
                # Recreate relative folder structure in trace/rules/
                relative_dir = rules_mk_path.parent.resolve().relative_to(self.src_dir.resolve())
                trace_rules_subdir = self.trace_dir / "rules" / relative_dir
                trace_rules_subdir.mkdir(parents=True, exist_ok=True)
                shutil.copy(rules_mk_build_path, trace_rules_subdir / rules_mk_build_path.name)

        subdirs = list(map(lambda x: x.parents[0], rules_mk_paths))

        subdirs.sort(key=lambda x: len(x.parts))
        dir_var_map = {Path('.'): IBMiJson.from_values(self.iproj_json.tgt_ccsid, self.iproj_json.objlib)}

        def map_ibmi_json_var(path):
            if path != Path("."):
                dir_var_map[path] = IBMiJson.from_file(path / ".ibmi.json", dir_var_map[path.parents[0]])

        list(map(map_ibmi_json_var, subdirs))
        # Python timestamp checking for optimization
        all_rules = []
        special_char_files = {}
        # Determine filtering strategy and skip conditions
        filtered_rules_mk_paths, check_specific_targets, skip_timestamp_check = self._prepare_timestamp_check(
            rules_mk_paths, real_targets
        )
        if not skip_timestamp_check:
            for rules_mk_path in filtered_rules_mk_paths:
                rules_mk = RulesMk.from_file(rules_mk_path, str(self.src_dir), map(Path, self.iproj_json.include_path))
                dir_key = rules_mk_path.parent
                if dir_key not in dir_var_map:
                    continue
                objlib = dir_var_map[dir_key].build['objlib']
                objlib_path = Path(objlib_to_path(objlib, iasp=self.iasp))
                for rule in rules_mk.rules:
                    if not rule.source_file:
                        continue
                    escaped_target = escape_special_chars(rule.target)
                    # Skip if checking specific targets and this isn't one
                    if check_specific_targets and escaped_target not in self.targets:
                        continue
                    # Check if target has special characters using helper
                    if self._has_special_chars(rule.target):
                        # Special char file: Python checks timestamp
                        needs_rebuild = self._check_target_needs_rebuild(rule, objlib_path)
                        special_char_files[escaped_target] = needs_rebuild
                    # Add to all_rules after validation (only if source exists or not special char)
                    all_rules.append((rule, objlib_path, escaped_target))
            # Check transitive dependencies
            if special_char_files:
                changed = True
                while changed:
                    changed = False
                    for rule, objlib_path, escaped_target in all_rules:
                        # Only check up-to-date special char files for dependencies
                        if escaped_target not in special_char_files or special_char_files[escaped_target]:
                            continue
                        # Check if this target depends on something being rebuilt
                        source_file = self._unescape_special_chars(rule.source_file.replace('$(d)/', ''))
                        source_ext = source_file.upper().split('.')[-1]
                        # If source is an object dependency that needs rebuild, mark this target too
                        if source_ext in TARGET_TARGETGROUPS_MAPPING:
                            escaped_dependency = self._escape_special_chars_internal(source_file)
                            if escaped_dependency in special_char_files and special_char_files[escaped_dependency]:
                                special_char_files[escaped_target] = True
                                changed = True
            # Build final target list
            targets_to_build = self._build_final_target_list(all_rules, special_char_files)
            # Update self.targets
            if special_char_files:
                # Suppress Make's verbose output since Python already filtered special char files
                self.suppress_make_output = True
                if targets_to_build:
                    # Update targets with filtered list
                    self.targets = targets_to_build
                else:
                    print(colored("All targets up-to-date", Colors.OKGREEN))
                    self.skip_make = True
        # set build env variables based on iproj.json
        # if not include_path specified just use INCDIR(*NONE)
        #  otherwise use INCDIR('dir1' 'dir2')
        incdir = "*NONE"
        include_path = self.iproj_json.include_path
        # if include path is not empty or *NONE then wrap in single quotes
        if len(include_path) > 0 and [v.upper() for v in include_path] != ["*NONE"]:
            incdir = '\'' + '\' \''.join(include_path) + '\''
        elif len(include_path) == 1:
            incdir = include_path[0].upper()
        with target_file_path.open("w", encoding="utf8") as file:
            # Library names that include the hash symbol need to be
            # escaped otherwise make will treat characters after the
            # hash as a comment.
            #
            # This escaping is reversed in `crtfrmstmf.py`.
            escaped_curlib = self.iproj_json.curlib.replace("#", "\\#")
            escaped_pre_usr_libl = ' '.join(lib.replace("#", "\\#") for lib in self.iproj_json.pre_usr_libl)
            escaped_post_usr_libl = ' '.join(lib.replace("#", "\\#") for lib in self.iproj_json.post_usr_libl)
            # Generate target patterns from Python's TARGET_TARGETGROUPS_MAPPING
            target_patterns = get_target_patterns_for_makefile()
            file.write(f"""# This file is generated by makei, DO NOT EDIT.
# Modify .ibmi.json to override values

curlib := {escaped_curlib}
preUsrlibl := {escaped_pre_usr_libl}
postUsrlibl := {escaped_post_usr_libl}
INCDIR := {incdir}
unquotedINCDIR := {' '.join(include_path)}
doublequotedINCDIR := {incdir.replace("'", "''")}
IBMiEnvCmd := {self.ibmi_env_cmds}
iasp := {self.iasp}
COLOR_TTY := {'true' if self.color else 'false'}

OBJECT_TARGET_PATTERNS := {target_patterns}

""")
            for subdir in subdirs:
                # print(dir_var_map[subdir].build)
                file.write(
                    f"TGTCCSID_{subdir.absolute()} := {dir_var_map[subdir].build['tgt_ccsid']}\n")
                file.write(
                    f"OBJPATH_{subdir.absolute()} := "
                    f"{objlib_to_path(dir_var_map[subdir].build['objlib'], iasp=self.iasp)}\n")

            # for rules_mk in rules_mks:
            #     with rules_mk.open('r') as rules_mk_file:
            #         lines = rules_mk_file.readlines()
            #         for line in lines:
            #             line = line.rstrip()
            #             if line and not line.startswith("#") \
            #                     and not "=" in line and not line.startswith((' ', '\t')):
            #                 file.write(
            #                     f"{line.split(':')[0]}_d := {rules_mk.parents[0].absolute()}\n")

    def make(self):
        """ Generate and execute the make command."""
        # Skip make if all targets are up-to-date
        if self.skip_make:
            self._post_make()
            return True
        if (self.src_dir / ".logs" / "joblog.json").exists():
            (self.src_dir / ".logs" / "joblog.json").unlink()
        if (self.src_dir / ".logs" / "output.log").exists():
            (self.src_dir / ".logs" / "output.log").unlink()

        def handle_make_output(line_bytes: bytes):
            if isinstance(line_bytes, bytes):
                line = line_bytes.decode(sys.getdefaultencoding())
            if "Failed to create" in line:
                self.failed_targets.append(line.split()[-1].split("!")[0])
            if "was created successfully!" in line:
                self.success_targets.append(line.split()[1])
            if "End of creating" in line:
                self.success_targets.append(line.split()[-1].split("!")[0])
            # Replace escaped special characters back to original symbols for display
            display_line = self._unescape_special_chars(line)
            print_to_stdout(display_line)

        # Generate command (returns tuple: display_cmd, actual_cmd)
        display_cmd, actual_cmd = self.generate_make_cmd()
        # Print display version, execute actual version
        print(colored(f">> {display_cmd}", Colors.OKGREEN))
        sys.stdout.flush()
        exit_code = run_command(actual_cmd, handle_make_output, echo_cmd=False)

        custom_makefile = os.environ.get('TOBI_CUSTOM_MAKEFILE')
        if custom_makefile and not self.success_targets and not self.failed_targets:
            if self.targets and self.targets[0] != "all":
                if exit_code == 0:
                    self.success_targets.append(self.targets[0])
                else:
                    self.failed_targets.append(self.targets[0])
        self._post_make()
        return not self.failed_targets

    def _post_make(self):
        for tmp_file in self.tmp_files:
            tmp_file.unlink(missing_ok=True)
        lock_path = self.src_dir / ".logs" / "joblog.lock"
        lock_path.unlink(missing_ok=True)
        print(colored("Objects:            ", Colors.BOLD), colored(f"{len(self.failed_targets)} failed", Colors.FAIL),
              colored(f"{len(self.success_targets)} succeed", Colors.OKGREEN),
              f"{len(self.success_targets) + len(self.failed_targets)} total")
        if self.failed_targets:
            print(" > Failed objects:   ", " ".join(self.failed_targets))
            print(colored("Build Failed!", Colors.FAIL))
        elif self.success_targets:
            print(colored("Build Successful!", Colors.OKGREEN))
        else:
            print(colored("All targets up-to-date", Colors.OKGREEN))
        # event_files = list(Path(".evfevent").rglob("*.evfevent"))

        # def replace_abs_path(line: str) -> str:
        #     if str(Path.cwd()) in line:
        #         line = line.replace(f'{Path.cwd()}/', '')
        #         new_len = len(line.split()[5])
        #         # Replace length
        #         line = line[:24] + f"{new_len:03d}" + line[27:]
        #         return line
        #     else:
        #         return line

        # for filepath in event_files:
        #     replace_file_content(filepath, replace_abs_path)
