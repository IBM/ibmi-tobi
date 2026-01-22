#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

import os
import re
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, TYPE_CHECKING

from makei.const import (FILE_TARGETGROUPS_MAPPING, TARGET_GROUPS, TARGET_TARGETGROUPS_MAPPING, MEMBER_TEXT_LINES,
                         METADATA_HEADER, TEXT_HEADER)
from makei.utils import decompose_filename, is_source_file, check_keyword_in_file, get_line, get_style_dict

if TYPE_CHECKING:
    from makei.build import BuildEnv


class MKRule:
    """Class representing a make rule"""
    target: str
    dependencies: List[str]
    commands: List[str]
    variables: List[str]
    containing_dir: Path
    include_dirs: List[Path]

    is_source_file: bool
    source_file: Optional[str] = None

    def __init__(self, target: str, dependencies: List[str], commands: List[str], variables: List[str],
                 containing_dir: Path, include_dirs: List[Path]):
        # pylint: disable=too-many-arguments

        self.target = target.upper()
        self.dependencies = dependencies
        self.commands = list(filter(lambda command: command.strip(), commands))
        self.variables = variables
        self.containing_dir = containing_dir
        self.include_dirs = include_dirs
        self.is_source_file = False

        if len(self.commands) == 0:
            for dependency in self.dependencies:
                if is_source_file(dependency) and decompose_filename(dependency)[-1] == "":
                    if (self.containing_dir / dependency).exists():
                        self.is_source_file = True
                        self.source_file = '$(d)/' + dependency
                        self.dependencies.remove(dependency)
                        return
            try:
                self.source_file = self.dependencies[0]
                self.dependencies.remove(self.source_file)
            except IndexError:
                print(f"No source file found for {self.target} in {self.dependencies}")
        else:
            self.commands.insert(0, f"@$(call echo_cmd,=== Creating [{self.target}] from custom recipe)")
            self.commands.append(f"@$(call echo_success_cmd,End of creating {self.target})")

    def __str__(self):
        variable_assignment = ''.join(f"{self.target}: {variable}\n" for variable in self.variables)
        if len(self.commands) > 0:
            return f"{self.target}_CUSTOM_RECIPE=true" + '\n' + f"{self.target} : " \
                                                                f"{' '.join(self._parse_dependencies())}" + '\n' + \
                ''.join(
                    ['\t' + cmd + '\n' for cmd in self.commands]) + variable_assignment
        try:
            target_type = self.target.split(".")[-1].upper()
            source_file = decompose_filename(self.source_file)[2].upper()
            if target_type in ("SQL", "MSGF"):
                recipe_name = f"{target_type}_RECIPE"
            elif target_type in ("PGM") and source_file in ("RPGLE", "SQLRPGLE"):
                recipe_name = target_type + '.' + source_file + '_TO_' + self.target.split(".")[
                    -1].upper() + '_RECIPE'
            else:
                recipe_name = decompose_filename(self.source_file)[2].upper() + '_TO_' + self.target.split(".")[
                    -1].upper() + '_RECIPE'
            return f"{self.target}_SRC={self.source_file}" + '\n' + f"{self.target}_DEP" \
                                                                    f"={' '.join(self.dependencies)}" + '\n' + \
                f"{self.target}_RECIPE={recipe_name}" + '\n' + variable_assignment
        except AttributeError:
            print(f"No source file found for {self.target}")
            sys.exit(1)

    def __repr__(self):
        return str(self)

    def _parse_dependencies(self) -> List[str]:
        """Parses the dependencies of a rule"""
        result = []
        for dependency in self.dependencies:
            if is_source_file(dependency) and decompose_filename(dependency)[-1] == "":
                if (self.containing_dir / dependency).exists():
                    result.append('$(d)/' + dependency)
                else:
                    for include_dir in self.include_dirs:
                        if (include_dir / dependency).exists():
                            result.append(str(include_dir / dependency))
                            break
                    result.append(dependency)
            else:
                result.append(dependency)
        return result

    def __eq__(self, other):
        if isinstance(other, MKRule):
            return (self.target == other.target and self.commands == other.commands and
                    self.dependencies == other.dependencies and self.variables == other.variables and
                    self.containing_dir == other.containing_dir)

        return False

    @staticmethod
    def from_str(rule_str: str, containing_dir: Path, include_dirs: List[Path]) -> "MKRule":
        r"""Creates a MKRule object from a string

        >>> rule_str = "target : dependency1 dependency2\n\tcommand1 param1 param2\n\tcommand2 param3 param4\n"
        >>> rule = MKRule.from_str(rule_str)
        >>> rule.target
        'target'
        >>> rule.dependencies
        ['dependency1', 'dependency2']
        >>> rule.commands
        ['command1 param1 param2', 'command2 param3 param4']
        >>> str(rule)
        'target : dependency1 dependency2\n\tcommand1 param1 param2\n\tcommand2 param3 param4\n'
        """
        rule_regex = re.compile(
            r"^(?P<target>\S+)[ \t]*:(?!=)[ \t]*(?P<dependencies>(?:[^\n]*)*)\n" +
            r"(?P<cmds>(?:[^\S\r\n]+?\S[^\n]*\n?|\s*\n)*)$")
        target_match = rule_regex.match(rule_str)
        if target_match:
            target = target_match.group("target")
            dependencies = target_match.group("dependencies").split()
            commands = list(
                filter(lambda cmd: cmd, map(lambda cmd: cmd.strip(), target_match.group("cmds").split('\n'))))
        else:
            raise ValueError(f"Invalid rule string '{rule_str}'")

        return MKRule(target, dependencies, commands, [], containing_dir, include_dirs)


class RulesMk:
    """A Class representing the rules.mk structure
    """
    containing_dir: Path
    subdirs: List[str]
    targets: Dict[str, List[str]]
    rules: List[MKRule]
    build_context: Optional['BuildEnv'] = None
    src_obj_mapping: Dict[str, str]

    def __init__(self, subdirs: List[str], rules: List[MKRule], containing_dir: Path) -> None:
        self.targets = {tgt_group + 's': [] for tgt_group in TARGET_GROUPS}
        self.src_obj_mapping = {}
        for rule in rules:
            if rule.source_file is not None:
                decomposed_src = decompose_filename(rule.source_file)
                src = f"{decomposed_src[0].upper()}.{decomposed_src[2].upper()}"
                if src not in self.src_obj_mapping:
                    self.src_obj_mapping[src] = [rule.target]
                else:
                    self.src_obj_mapping[src].append(rule.target)
                tgt_group_list = FILE_TARGETGROUPS_MAPPING[decomposed_src[-2].upper()]

                # If only 1 target mapping exists, use it, otherwise use target's extension
                tgt_group = (next(iter(tgt_group_list)).upper() if len(tgt_group_list) == 1
                             else rule.target.split('.')[-1].upper())
                if tgt_group not in TARGET_GROUPS:
                    print(f"Warning: Target '{rule.target}' is not supported")
                    sys.exit(1)

                self.targets[tgt_group + 's'].append(rule.target)
            else:
                try:
                    tgt_group = TARGET_TARGETGROUPS_MAPPING[rule.target.split('.')[-1]]
                except KeyError:
                    print(f"Warning: Target '{rule.target}' is not supported")
                    sys.exit(1)

                self.targets[tgt_group + 's'].append(rule.target)

        if len(subdirs) > 0:
            nestedDirs = os.listdir(containing_dir)

            # Mapping from lowercase of directory name to the actual directory name
            # Assumes that we can't have two mixed case directory names
            dirLowerDict = dict(zip([dir.lower() for dir in nestedDirs], nestedDirs))

            for i in range(len(subdirs)):
                dir = dirLowerDict.get(subdirs[i].lower())

                if dir is not None:
                    subdirs[i] = dir
        self.subdirs = subdirs
        self.rules = rules
        self.containing_dir = containing_dir

    # Read makefile and create a RulesMk object
    @classmethod
    def from_file(cls, rules_mk_path: Path, src_dir: str, include_dirs=None) -> "RulesMk":
        if include_dirs is None:
            include_dirs = []
        with rules_mk_path.open("r") as f:
            rules_mk_str = f.read()
        rules_mk = RulesMk.from_str(rules_mk_str, rules_mk_path.parent, src_dir, include_dirs)
        return rules_mk

    @classmethod
    def from_str(cls, rules_mk_str: str, containing_dir: Path, src_dir: Path, include_dirs=None) -> "RulesMk":
        """Creates a RulesMk object from a string

        >>> rules_mk_str = "subdir1 subdir2\n\n\ttarget1 target2\n\n\ttarget3 target4\n\n\ttarget5 target6\n"
        >>> rules_mk = RulesMk.from_str(rules_mk_str)
        >>> rules_mk.subdirs
        ['subdir1', 'subdir2']
        >>> rules_mk.targets
        {'all': ['target1', 'target2', 'target3', 'target4', 'target5', 'target6'], 'install': ['target1', 'target2',
        'target3', 'target4', 'target5', 'target6']}
        """
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-branches

        if include_dirs is None:
            include_dirs = []

        rules = []
        rules_mk_variables = {}
        variables = {}
        wildcard_variables = {}
        subdir = []
        targets = []
        wildcard_targets = []

        recipe_env = False
        recipe_str = ""
        dir_path = src_dir.joinpath(containing_dir)  # directory with the source code

        # Handle multiline continuation lines that end in a backslash ('\')
        lines = []
        current_line = ""
        for line in rules_mk_str.split('\n'):
            stripped_line = line.rstrip()
            if stripped_line.endswith("\\"):
                # Continuation line
                current_line += stripped_line.rstrip(" \\") + " "
            else:
                # Single line or last line of a continuation line
                if current_line == "":
                    current_line += stripped_line
                else:
                    current_line += stripped_line.lstrip()
                lines.append(current_line)
                current_line = ""

        for line in lines:
            if recipe_env:
                if re.match(r'\s', line):
                    recipe_str += line + '\n'
                    continue

                targets.append(recipe_str.split(":")[0].upper())
                rules.append(MKRule.from_str(recipe_str, containing_dir, include_dirs))
                recipe_env = False
                recipe_str = ""

            if line.startswith('#') or line == '':
                # Comment line or empty line
                continue

            # pylint: disable=no-else-continue
            # Match strings that start with any sequence of characters (except ':'),
            # followed by either ':=' or '=', and then any characters afterwards
            pattern = re.compile(r'^[^:]*(:=|=).*')
            if line.strip().startswith('SUBDIRS'):
                # Subdir definition
                subdir = line.strip().split('=')[1].split()
                continue
            elif pattern.match(line):
                # rules_mk variable definition (ie. var := value)
                line_split_by_equal = line.strip().split('=')
                if len(line_split_by_equal) == 2:
                    rules_mk_var = line_split_by_equal[0].rstrip(" :")
                    rules_mk_var_value = line_split_by_equal[1].strip()
                    rules_mk_variables[rules_mk_var] = rules_mk_var_value
            elif ':' in line:
                # Recipe declaration
                if '=' in line:
                    # private variable definition
                    target, variable = line.strip().split(':', 1)
                    if target.startswith("%."):
                        variables_to_process = wildcard_variables
                    else:
                        variables_to_process = variables

                    key = target.strip().upper()
                    variable = variable.strip()
                    if key not in variables_to_process:
                        variables_to_process[key] = []
                    # Replace instances of rules_mk variables with their actual values
                    var_split = variable.split('=')
                    wrapped_var_key = var_split[-1].strip(" ")  # Potential variable key wrapped in "$(" and ")"
                    if wrapped_var_key.startswith("$(") and wrapped_var_key.endswith(")"):
                        rules_mk_var = wrapped_var_key[2:-1]  # Remove leading $( and trailing )
                        if rules_mk_var in rules_mk_variables:
                            var_split[0] = var_split[0].rstrip()
                            var_split[-1] = rules_mk_variables[rules_mk_var]
                            variable = "=".join(var_split)

                    variables_to_process[key].append(variable)
                else:
                    # Wildcard %.TARGET: %.SOURCE DEP1 DEP2
                    line_split_by_space = line.strip().split()
                    if line_split_by_space[0].startswith("%.") and line_split_by_space[1].startswith("%."):
                        wildcard_targets.append(
                            (line_split_by_space[0].strip("%.").strip(":").upper(),
                             line_split_by_space[1].strip("%.").lower(),
                             ' '.join(line_split_by_space[2:]) if len(line_split_by_space) > 2 else '')
                             )
                    else:
                        # recipe
                        recipe_env = True
                        recipe_str = line + '\n'
                continue
            else:
                # print(f"Skipped line {line}")
                continue

        if recipe_env:
            targets.append(recipe_str.split(":")[0].upper())
            rules.append(MKRule.from_str(recipe_str, containing_dir, include_dirs))

        # Create all the rules for the wildcard rule declaration
        for target_ext, source_ext, dependencies in wildcard_targets:
            # Expand any variables in the dependencies
            expanded_deps = dependencies
            for var_name, var_value in rules_mk_variables.items():
                expanded_deps = expanded_deps.replace(f"$({var_name})", var_value)
            # target specific variable assignmnet(expansion)
            for filename in os.listdir(dir_path):
                recipe_str = ''
                filename_split = filename.split('.', 1)

                if filename_split[-1].lower() == source_ext:
                    target_object = (filename_split[0] + "." + target_ext).upper()
                    if target_object not in targets:
                        recipe_str = (
                            target_object + ": " + filename_split[0] + "." + source_ext + " " + expanded_deps
                        ).strip() + '\n'
                        rules.append(MKRule.from_str(recipe_str, containing_dir, include_dirs))
                        targets.append(target_object)

        # Updates variables with wildcard values
        for wildcard, var in wildcard_variables.items():
            stripped_wildcard = wildcard.strip("%.").upper()
            matched_targets = [target for target in targets if target.endswith(f".{stripped_wildcard}")]
            targets = list(filter(lambda target: target.split(".")[1] != stripped_wildcard, targets))

            for target in matched_targets:
                if target not in variables:
                    variables[target] = []
                variables[target] = var + variables[target]

        # Defines variables declared in Rules.mk
        for target, variableList in variables.items():
            matched_rules = filter(lambda rule: rule.target.upper() == target, rules)
            for rule in matched_rules:
                rule.variables = variableList

        for rule in rules:
            if rule.is_source_file:
                source_location = dir_path.joinpath(rule.source_file.rsplit("/", 1)[-1])
                is_text_defined = RulesMk._find_source_member_text(source_location)

                # Overrides member text defined in Rules.mk if comment at top of source
                if is_text_defined is not None:
                    rule.variables.append('TEXT = ' + is_text_defined)

        return RulesMk(subdir, rules, containing_dir)

    @classmethod
    def _remove_comment_identifier(cls, text: str, file_path: Path) -> str:
        style_dict = get_style_dict(file_path)
        if style_dict is not None:
            start_comment = style_dict["start_comment"]
            end_comment = style_dict["end_comment"]
            text = text.strip(" " + start_comment).strip(end_comment).strip(TEXT_HEADER).strip()
        return text

    # Will Return the member text if it exists, otherwise
    @classmethod
    def _find_source_member_text(cls, file_path: Path) -> str:
        metadata_comment_exists = check_keyword_in_file(file_path, METADATA_HEADER, MEMBER_TEXT_LINES)
        if metadata_comment_exists:
            text_comment_exists = check_keyword_in_file(file_path, TEXT_HEADER, MEMBER_TEXT_LINES,
                                                        metadata_comment_exists)
            if text_comment_exists and text_comment_exists > metadata_comment_exists:
                text_line = get_line(file_path, text_comment_exists)
                if text_line is not None:
                    text = RulesMk._remove_comment_identifier(text_line, file_path)
                    return text

        return None

    def __str__(self, rules_middleware: Callable[[MKRule], MKRule] = lambda rule: rule) -> str:
        """Returns a string representation of the RulesMk object
        """
        rules_str = ""
        if len(self.subdirs) > 0:
            rules_str += "SUBDIRS := " + " ".join(self.subdirs) + "\n\n"

        for target_group, targets in self.targets.items():
            if len(targets) > 0:
                rules_str += f"{target_group} := {' '.join(targets)}\n"
        rules_str += "\n\n"
        rules_str += ''.join(map(str, map(rules_middleware, self.rules)))
        return rules_str


if __name__ == "__main__":
    # print(RulesMk.from_file(Path("/Users/tongkun/git/tobi-example/QDDSSRC/Rules.mk")))
    # print(str(RulesMk.from_file(Path("/Users/tongkun/git/tobi-example/functionsVAT/Rules.mk"))))
    import doctest

    doctest.testmod()
