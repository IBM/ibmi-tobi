from makei.rules_mk import RulesMk, MKRule
from tests.lib.const import DATA_PATH

data_dir = DATA_PATH / "rules_mks"

# Test use %.MODULE wildcards and variables
# TGTVER := *PRV
# CURRENT:=V7R5
# HEADER := some

# # test base wildcard with variables
# %.MODULE: %.rpgle $(HEADER).rpgleinc
# # test case sensitivity and overriding
# Foo.MODULE: TGTVER=$(CURRENT)
# # override different var
# %.MODULE: TEXT := hardcoded TEXT
# foo.MODULE: private TEXT := foo is better
# foo.MODULE: TGTVER := V7R2
# # now support multi line dependencies
# %.PGM: %.pgm.rpgle \
#        DB1.FILE


def test_wildcard_recipes_variables():
    # Test loading from a valid file
    test_dir = data_dir / "wildcard"
    rules_mk = RulesMk.from_file(test_dir / "wildcard.rules.mk", test_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": [],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": ["BAR.MODULE", "AB2001_B.MODULE", "AB2001.B.MODULE", "FOO.MODULE"],
        "SRVPGMs": [],
        "PGMs": [],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }
    assert rules_mk.containing_dir == test_dir
    assert rules_mk.subdirs == []
    assert rules_mk.targets == expected_targets

    assert rules_mk.rules[0].variables == [
        "TEXT := hardcoded for all mod",
        "COMMIT=*NONE",
        "TGTVER:=V7R3",
    ]
    assert rules_mk.rules[0].commands == []
    assert rules_mk.rules[0].dependencies == ["bar.TABLE"]
    assert rules_mk.rules[0].include_dirs == []
    assert rules_mk.rules[0].target == "BAR.MODULE"
    assert rules_mk.rules[0].source_file == "$(d)/bar.rpgle"
    assert (
        str(rules_mk.rules[0])
        == """BAR.MODULE_SRC=$(d)/bar.rpgle
BAR.MODULE_DEP=bar.TABLE
BAR.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE
BAR.MODULE: TEXT := hardcoded for all mod
BAR.MODULE: COMMIT=*NONE
BAR.MODULE: TGTVER:=V7R3
"""
    )

    assert rules_mk.rules[1].variables == [
        "TEXT := hardcoded for all mod",
        "TGTRLS :=*PRV",
    ]
    assert rules_mk.rules[1].commands == []
    assert rules_mk.rules[1].dependencies == []
    assert rules_mk.rules[1].include_dirs == []
    assert rules_mk.rules[1].target == "AB2001_B.MODULE"
    assert rules_mk.rules[1].source_file == "$(d)/AB2001_B.rpgle"
    assert (
        str(rules_mk.rules[1])
        == """AB2001_B.MODULE_SRC=$(d)/AB2001_B.rpgle
AB2001_B.MODULE_DEP=
AB2001_B.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE
AB2001_B.MODULE: TEXT := hardcoded for all mod
AB2001_B.MODULE: TGTRLS :=*PRV
"""
    )

    assert rules_mk.rules[2].variables == [
        "TEXT := hardcoded for all mod",
        "TGTRLS :=*PRV",
    ]
    assert rules_mk.rules[2].commands == []
    assert rules_mk.rules[2].dependencies == []
    assert rules_mk.rules[2].include_dirs == []
    assert rules_mk.rules[2].target == "AB2001.B.MODULE"
    assert rules_mk.rules[2].source_file == "$(d)/AB2001.B.rpgle"
    assert (
        str(rules_mk.rules[2])
        == """AB2001.B.MODULE_SRC=$(d)/AB2001.B.rpgle
AB2001.B.MODULE_DEP=
AB2001.B.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE
AB2001.B.MODULE: TEXT := hardcoded for all mod
AB2001.B.MODULE: TGTRLS :=*PRV
"""
    )

    assert rules_mk.rules[3].variables == [
        "TEXT := hardcoded for all mod",
        "TGTVER=V7R5",
        "private TEXT := foo is better",
        "TGTVER := V7R2",
    ]
    assert rules_mk.rules[3].commands == []
    assert rules_mk.rules[3].dependencies == ["some.rpgleinc"]
    assert rules_mk.rules[3].include_dirs == []
    assert rules_mk.rules[3].target == "FOO.MODULE"
    assert rules_mk.rules[3].source_file == "$(d)/foo.rpgle"
    assert (
        str(rules_mk.rules[3])
        == """FOO.MODULE_SRC=$(d)/foo.rpgle
FOO.MODULE_DEP=some.rpgleinc
FOO.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE
FOO.MODULE: TEXT := hardcoded for all mod
FOO.MODULE: TGTVER=V7R5
FOO.MODULE: private TEXT := foo is better
FOO.MODULE: TGTVER := V7R2\n"""
    )

    assert (
        str(rules_mk)
        == """MODULEs := BAR.MODULE AB2001_B.MODULE AB2001.B.MODULE FOO.MODULE\n\n
BAR.MODULE_SRC=$(d)/bar.rpgle
BAR.MODULE_DEP=bar.TABLE
BAR.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE
BAR.MODULE: TEXT := hardcoded for all mod
BAR.MODULE: COMMIT=*NONE
BAR.MODULE: TGTVER:=V7R3
AB2001_B.MODULE_SRC=$(d)/AB2001_B.rpgle
AB2001_B.MODULE_DEP=
AB2001_B.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE
AB2001_B.MODULE: TEXT := hardcoded for all mod
AB2001_B.MODULE: TGTRLS :=*PRV
AB2001.B.MODULE_SRC=$(d)/AB2001.B.rpgle
AB2001.B.MODULE_DEP=
AB2001.B.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE
AB2001.B.MODULE: TEXT := hardcoded for all mod
AB2001.B.MODULE: TGTRLS :=*PRV
FOO.MODULE_SRC=$(d)/foo.rpgle
FOO.MODULE_DEP=some.rpgleinc
FOO.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE
FOO.MODULE: TEXT := hardcoded for all mod
FOO.MODULE: TGTVER=V7R5
FOO.MODULE: private TEXT := foo is better
FOO.MODULE: TGTVER := V7R2
"""
    )


def test_from_file():
    # Test loading from a valid file
    rules_mk = RulesMk.from_file(data_dir / "a.rules.mk", data_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": [],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": ["VAT300.MODULE"],
        "SRVPGMs": [],
        "PGMs": [],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }
    variables1 = [
        "private DFTACTGRP = *NO",
        "private TEXT := Andy is cool",
        "private VARSHELL ?= SHELL",
        "private VARAPPEND += TOAPPEND",
        "private VARAPPEND+=APPEND2 # we support end of line comments",
        "private VARIMMED ::= IMMED",
        "private VARESCAPE :::= ESCAPE",
    ]
    mkrule1 = MKRule(
        "VAT300.MODULE", ["vat300.rpgle", "some.rpgleinc"], [], variables1, data_dir, []
    )
    expected_rules = [mkrule1]

    assert rules_mk.src_obj_mapping["VAT300.RPGLE"] == ["VAT300.MODULE"]
    assert rules_mk.containing_dir == data_dir
    assert rules_mk.subdirs == ["adir", "bdir"]
    assert rules_mk.targets == expected_targets
    assert rules_mk.rules[0].variables == variables1
    assert rules_mk.rules[0] == expected_rules[0]
    assert rules_mk.build_context is None
    assert (
        str(mkrule1)
        == """VAT300.MODULE_SRC=vat300.rpgle\nVAT300.MODULE_DEP=some.rpgleinc
VAT300.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE
VAT300.MODULE: private DFTACTGRP = *NO
VAT300.MODULE: private TEXT := Andy is cool
VAT300.MODULE: private VARSHELL ?= SHELL
VAT300.MODULE: private VARAPPEND += TOAPPEND
VAT300.MODULE: private VARAPPEND+=APPEND2 # we support end of line comments
VAT300.MODULE: private VARIMMED ::= IMMED
VAT300.MODULE: private VARESCAPE :::= ESCAPE
"""
    )
    assert (
        str(rules_mk)
        == """SUBDIRS := adir bdir

MODULEs := VAT300.MODULE


VAT300.MODULE_SRC=vat300.rpgle
VAT300.MODULE_DEP=some.rpgleinc
VAT300.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE
VAT300.MODULE: private DFTACTGRP = *NO
VAT300.MODULE: private TEXT := Andy is cool
VAT300.MODULE: private VARSHELL ?= SHELL
VAT300.MODULE: private VARAPPEND += TOAPPEND
VAT300.MODULE: private VARAPPEND+=APPEND2 # we support end of line comments
VAT300.MODULE: private VARIMMED ::= IMMED
VAT300.MODULE: private VARESCAPE :::= ESCAPE
"""
    )


def test_custom_recipe():
    # Test loading from a valid file
    rules_mk = RulesMk.from_file(data_dir / "custom.rules.mk", data_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": ["CRTSBSD.FILE"],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": [],
        "SRVPGMs": [],
        "PGMs": [],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }
    commands0 = [
        "@$(call echo_cmd,=== Creating [CRTSBSD.FILE] from custom recipe)",
        'system -i "CRTSBSD SBSD(BATCHWL/BATCHSBSD) POOLS((1 *SHRPOOL3 *N *MB))"',
        "@$(call echo_success_cmd,End of creating CRTSBSD.FILE)",
    ]
    assert rules_mk.containing_dir == data_dir
    assert rules_mk.subdirs == []
    assert rules_mk.targets == expected_targets
    assert rules_mk.rules[0].variables == []
    assert rules_mk.rules[0].commands == commands0
    assert rules_mk.rules[0].dependencies == []
    assert rules_mk.rules[0].include_dirs == []
    assert rules_mk.rules[0].target == "CRTSBSD.FILE"
    assert rules_mk.rules[0].source_file is None
    assert rules_mk.build_context is None
    assert (
        str(rules_mk.rules[0])
        == """CRTSBSD.FILE_CUSTOM_RECIPE=true
CRTSBSD.FILE : \n\t@$(call echo_cmd,=== Creating [CRTSBSD.FILE] from custom recipe)
\tsystem -i "CRTSBSD SBSD(BATCHWL/BATCHSBSD) POOLS((1 *SHRPOOL3 *N *MB))"
\t@$(call echo_success_cmd,End of creating CRTSBSD.FILE)
"""
    )
    assert (
        str(rules_mk)
        == """PFs := CRTSBSD.FILE


CRTSBSD.FILE_CUSTOM_RECIPE=true
CRTSBSD.FILE : \n\t@$(call echo_cmd,=== Creating [CRTSBSD.FILE] from custom recipe)
\tsystem -i "CRTSBSD SBSD(BATCHWL/BATCHSBSD) POOLS((1 *SHRPOOL3 *N *MB))"
\t@$(call echo_success_cmd,End of creating CRTSBSD.FILE)
"""
    )


def test_dtaara_recipe():
    # Test loading from a valid file
    rules_mk = RulesMk.from_file(data_dir / "dtaara.rules.mk", data_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": ["LASTORDNO.DTAARA"],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": [],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": [],
        "SRVPGMs": [],
        "PGMs": [],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }

    assert rules_mk.src_obj_mapping["LASTORDNO.DTAARA"] == ["LASTORDNO.DTAARA"]
    assert rules_mk.containing_dir == data_dir
    assert rules_mk.subdirs == []
    assert rules_mk.targets == expected_targets

    assert rules_mk.rules[0].variables == []
    assert rules_mk.rules[0].commands == []
    assert rules_mk.rules[0].dependencies == []
    assert rules_mk.rules[0].include_dirs == []
    assert rules_mk.rules[0].target == "LASTORDNO.DTAARA"
    assert rules_mk.rules[0].source_file == "LASTORDNO.DTAARA"
    assert (
        str(rules_mk.rules[0])
        == """LASTORDNO.DTAARA_SRC=LASTORDNO.DTAARA
LASTORDNO.DTAARA_DEP=
LASTORDNO.DTAARA_RECIPE=DTAARA_TO_DTAARA_RECIPE\n"""
    )
    assert (
        str(rules_mk)
        == """DTAARAs := LASTORDNO.DTAARA\n\n
LASTORDNO.DTAARA_SRC=LASTORDNO.DTAARA
LASTORDNO.DTAARA_DEP=
LASTORDNO.DTAARA_RECIPE=DTAARA_TO_DTAARA_RECIPE
"""
    )


def test_dtaq_recipe():
    # Test loading from a valid file
    rules_mk = RulesMk.from_file(data_dir / "dtaq.rules.mk", data_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": ["ORDERS.DTAQ"],
        "SQLs": [],
        "BNDDs": [],
        "PFs": [],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": [],
        "SRVPGMs": [],
        "PGMs": [],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }

    assert rules_mk.src_obj_mapping["ORDERS.DTAQ"] == ["ORDERS.DTAQ"]
    assert rules_mk.containing_dir == data_dir
    assert rules_mk.subdirs == []
    assert rules_mk.targets == expected_targets

    assert rules_mk.rules[0].variables == []
    assert rules_mk.rules[0].commands == []
    assert rules_mk.rules[0].dependencies == []
    assert rules_mk.rules[0].include_dirs == []
    assert rules_mk.rules[0].target == "ORDERS.DTAQ"
    assert rules_mk.rules[0].source_file == "ORDERS.DTAQ"
    assert (
        str(rules_mk.rules[0])
        == """ORDERS.DTAQ_SRC=ORDERS.DTAQ
ORDERS.DTAQ_DEP=
ORDERS.DTAQ_RECIPE=DTAQ_TO_DTAQ_RECIPE\n"""
    )
    assert (
        str(rules_mk)
        == """DTAQs := ORDERS.DTAQ\n\n
ORDERS.DTAQ_SRC=ORDERS.DTAQ
ORDERS.DTAQ_DEP=
ORDERS.DTAQ_RECIPE=DTAQ_TO_DTAQ_RECIPE
"""
    )


def test_pfsql_recipe():
    # Test loading from a valid file
    rules_mk = RulesMk.from_file(data_dir / "pfsql.rules.mk", data_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": ["CUSTINFO1.FILE", "CUSTINFO.FILE", "LOWER.FILE"],
        "BNDDs": [],
        "PFs": [],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": [],
        "SRVPGMs": [],
        "PGMs": [],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }

    assert rules_mk.containing_dir == data_dir
    assert rules_mk.subdirs == []
    assert rules_mk.targets == expected_targets
    assert rules_mk.rules[0].variables == []
    assert rules_mk.rules[0].commands == []
    assert rules_mk.rules[0].dependencies == []
    assert rules_mk.rules[0].include_dirs == []
    assert rules_mk.rules[0].target == "CUSTINFO1.FILE"
    assert rules_mk.rules[0].source_file == "CUSTINFO1.PFSQL"
    assert (
        str(rules_mk.rules[0])
        == """CUSTINFO1.FILE_SRC=CUSTINFO1.PFSQL
CUSTINFO1.FILE_DEP=
CUSTINFO1.FILE_RECIPE=PFSQL_TO_FILE_RECIPE\n"""
    )
    assert (
        str(rules_mk)
        == """SQLs := CUSTINFO1.FILE CUSTINFO.FILE LOWER.FILE\n\n
CUSTINFO1.FILE_SRC=CUSTINFO1.PFSQL
CUSTINFO1.FILE_DEP=
CUSTINFO1.FILE_RECIPE=PFSQL_TO_FILE_RECIPE
CUSTINFO.FILE_SRC=CUSTINFO.TABLE
CUSTINFO.FILE_DEP=
CUSTINFO.FILE_RECIPE=TABLE_TO_FILE_RECIPE
LOWER.FILE_SRC=lower.pfsql
LOWER.FILE_DEP=
LOWER.FILE_RECIPE=PFSQL_TO_FILE_RECIPE
"""
    )


def test_dds_recipe():
    # Test loading from a valid file
    rules_mk = RulesMk.from_file(data_dir / "dds.rules.mk", data_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": ["ARTICLE.FILE", "DETORD.FILE", "TMPDETORD.FILE"],
        "LFs": [],
        "DSPFs": ["ART301D.FILE"],
        "PRTFs": ["ORD500O.FILE"],
        "CMDs": [],
        "MODULEs": [],
        "SRVPGMs": [],
        "PGMs": [],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }
    assert rules_mk.src_obj_mapping["ARTICLE.PF"] == ["ARTICLE.FILE"]
    assert rules_mk.src_obj_mapping["ART301D.DSPF"] == ["ART301D.FILE"]
    assert rules_mk.src_obj_mapping["DETORD.PF"] == ["DETORD.FILE"]
    assert rules_mk.src_obj_mapping["ORD500O.PRTF"] == ["ORD500O.FILE"]
    assert rules_mk.containing_dir == data_dir
    assert rules_mk.subdirs == []
    assert rules_mk.targets == expected_targets
    assert rules_mk.rules[0].variables == []
    assert rules_mk.rules[0].commands == []
    assert rules_mk.rules[0].dependencies == ["SAMREF.FILE"]
    assert rules_mk.rules[0].include_dirs == []
    assert rules_mk.rules[0].target == "ARTICLE.FILE"
    assert rules_mk.rules[0].source_file == "ARTICLE-Article_File.PF"
    assert (
        str(rules_mk.rules[0])
        == """ARTICLE.FILE_SRC=ARTICLE-Article_File.PF\nARTICLE.FILE_DEP=SAMREF.FILE
ARTICLE.FILE_RECIPE=PF_TO_FILE_RECIPE\n"""
    )

    assert rules_mk.rules[1].variables == ["DFRWRT = *NO", "ENHDSP = *NO"]
    assert rules_mk.rules[1].commands == []
    assert rules_mk.rules[1].dependencies == ["ARTICLE.FILE", "VATDEF.FILE"]
    assert rules_mk.rules[1].include_dirs == []
    assert rules_mk.rules[1].target == "ART301D.FILE"
    assert rules_mk.rules[1].source_file == "ART301D-Function_Select_an_article.DSPF"
    assert (
        str(rules_mk.rules[1])
        == """ART301D.FILE_SRC=ART301D-Function_Select_an_article.DSPF
ART301D.FILE_DEP=ARTICLE.FILE VATDEF.FILE\nART301D.FILE_RECIPE=DSPF_TO_FILE_RECIPE
ART301D.FILE: DFRWRT = *NO\nART301D.FILE: ENHDSP = *NO\n"""
    )

    assert rules_mk.rules[4].variables == []
    assert rules_mk.rules[4].commands == [
        "@$(call echo_cmd,=== Creating [TMPDETORD.FILE] from custom recipe)",
        'system -i "CPYF FROMFILE($(OBJLIB)/DETORD) TOFILE($(OBJLIB)/TMPDETORD) CRTFILE(*YES)"',
        "@$(call echo_success_cmd,End of creating TMPDETORD.FILE)",
    ]
    assert rules_mk.rules[4].dependencies == []
    assert rules_mk.rules[4].include_dirs == []
    assert rules_mk.rules[4].target == "TMPDETORD.FILE"
    assert rules_mk.rules[4].source_file is None
    assert (
        str(rules_mk.rules[4])
        == """TMPDETORD.FILE_CUSTOM_RECIPE=true
TMPDETORD.FILE : \n\t@$(call echo_cmd,=== Creating [TMPDETORD.FILE] from custom recipe)
\tsystem -i "CPYF FROMFILE($(OBJLIB)/DETORD) TOFILE($(OBJLIB)/TMPDETORD) CRTFILE(*YES)"
\t@$(call echo_success_cmd,End of creating TMPDETORD.FILE)\n"""
    )

    assert (
        str(rules_mk)
        == """PFs := ARTICLE.FILE DETORD.FILE TMPDETORD.FILE
DSPFs := ART301D.FILE
PRTFs := ORD500O.FILE\n\n
ARTICLE.FILE_SRC=ARTICLE-Article_File.PF\nARTICLE.FILE_DEP=SAMREF.FILE
ARTICLE.FILE_RECIPE=PF_TO_FILE_RECIPE
ART301D.FILE_SRC=ART301D-Function_Select_an_article.DSPF
ART301D.FILE_DEP=ARTICLE.FILE VATDEF.FILE
ART301D.FILE_RECIPE=DSPF_TO_FILE_RECIPE\nART301D.FILE: DFRWRT = *NO\nART301D.FILE: ENHDSP = *NO
DETORD.FILE_SRC=DETORD.PF
DETORD.FILE_DEP=SAMREF.FILE
DETORD.FILE_RECIPE=PF_TO_FILE_RECIPE\nORD500O.FILE_SRC=ORD500O.PRTF
ORD500O.FILE_DEP=ORDER.FILE CUSTOMER.FILE DETORD.FILE ARTICLE.FILE
ORD500O.FILE_RECIPE=PRTF_TO_FILE_RECIPE\nTMPDETORD.FILE_CUSTOM_RECIPE=true
TMPDETORD.FILE : \n\t@$(call echo_cmd,=== Creating [TMPDETORD.FILE] from custom recipe)
\tsystem -i "CPYF FROMFILE($(OBJLIB)/DETORD) TOFILE($(OBJLIB)/TMPDETORD) CRTFILE(*YES)"
\t@$(call echo_success_cmd,End of creating TMPDETORD.FILE)
"""
    )


def test_src_obj_mapping():
    rules_mk = RulesMk.from_file(data_dir / "mapping.rules.mk", data_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": [],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": ["OBSCURE.MODULE", "HELLO.MODULE"],
        "SRVPGMs": [],
        "PGMs": ["HELLO.PGM", "WORLD.PGM"],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }
    assert rules_mk.src_obj_mapping["LONGSOURCEFILENAME.RPGLE"] == ["OBSCURE.MODULE"]
    assert rules_mk.src_obj_mapping["HELLO.RPGLE"] == ["HELLO.PGM", "HELLO.MODULE"]
    assert rules_mk.src_obj_mapping["WORLD.PGM.RPGLE"] == ["WORLD.PGM"]
    assert rules_mk.containing_dir == data_dir
    assert rules_mk.subdirs == []
    assert rules_mk.targets == expected_targets

    assert rules_mk.rules[0].variables == []
    assert rules_mk.rules[0].commands == []
    assert rules_mk.rules[0].dependencies == []
    assert rules_mk.rules[0].include_dirs == []
    assert rules_mk.rules[0].target == "OBSCURE.MODULE"
    assert rules_mk.rules[0].source_file == "LONGSOURCEFILENAME.RPGLE"
    assert (
        str(rules_mk.rules[0])
        == """OBSCURE.MODULE_SRC=LONGSOURCEFILENAME.RPGLE
OBSCURE.MODULE_DEP=\nOBSCURE.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE\n"""
    )

    assert rules_mk.rules[1].variables == []
    assert rules_mk.rules[1].commands == []
    assert rules_mk.rules[1].dependencies == []
    assert rules_mk.rules[1].include_dirs == []
    assert rules_mk.rules[1].target == "HELLO.PGM"
    assert rules_mk.rules[1].source_file == "HELLO.RPGLE"
    # assert str(rules_mk.rules[1]) == '''HELLO.PGM_SRC=HELLO.RPGLE\nHELLO.PGM_DEP=
    # HELLO.PGM_RECIPE=PGM.RPGLE_TO_PGM_RECIPE\n'''
    assert rules_mk.rules[2].variables == []
    assert rules_mk.rules[2].commands == []
    assert rules_mk.rules[2].dependencies == []
    assert rules_mk.rules[2].include_dirs == []
    assert rules_mk.rules[2].target == "HELLO.MODULE"
    assert rules_mk.rules[2].source_file == "HELLO.RPGLE"
    assert (
        str(rules_mk.rules[2])
        == """HELLO.MODULE_SRC=HELLO.RPGLE\nHELLO.MODULE_DEP=
HELLO.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE\n"""
    )

    assert rules_mk.rules[3].variables == []
    assert rules_mk.rules[3].commands == []
    assert rules_mk.rules[3].dependencies == []
    assert rules_mk.rules[3].include_dirs == []
    assert rules_mk.rules[3].target == "WORLD.PGM"
    assert rules_mk.rules[3].source_file == "WORLD.PGM.RPGLE"
    assert (
        str(rules_mk.rules[3])
        == """WORLD.PGM_SRC=WORLD.PGM.RPGLE\nWORLD.PGM_DEP=
WORLD.PGM_RECIPE=PGM.RPGLE_TO_PGM_RECIPE\n"""
    )


def test_src_obj_mapping_from_root_folder():
    # Test loading from a valid file
    test_dir = DATA_PATH / "build_env" / "sample_project1"
    rules_mk = RulesMk.from_file(test_dir / "Rules.mk", test_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": [],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": ["HELLO.MODULE"],
        "SRVPGMs": [],
        "PGMs": [],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }
    assert rules_mk.src_obj_mapping["HELLOP.RPGLE"] == ["HELLO.MODULE"]
    assert rules_mk.containing_dir == test_dir
    assert rules_mk.subdirs == ["inner"]
    assert rules_mk.targets == expected_targets

    assert rules_mk.rules[0].variables == []
    assert rules_mk.rules[0].commands == []
    assert rules_mk.rules[0].dependencies == []
    assert rules_mk.rules[0].include_dirs == []
    assert rules_mk.rules[0].target == "HELLO.MODULE"
    assert (
        str(rules_mk)
        == """SUBDIRS := inner

MODULEs := HELLO.MODULE


HELLO.MODULE_SRC=$(d)/HELLOP.RPGLE
HELLO.MODULE_DEP=
HELLO.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE
"""
    )


def test_src_obj_mapping_from_subfolder():
    # Test loading from a valid file
    test_dir = DATA_PATH / "build_env" / "sample_project1" / "innerdir1"
    rules_mk = RulesMk.from_file(test_dir / "Rules.mk", test_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": [],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": ["TESTX.MODULE"],
        "SRVPGMs": [],
        "PGMs": [],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }
    assert rules_mk.src_obj_mapping["TEST.SQLRPGLE"] == ["TESTX.MODULE"]
    assert rules_mk.containing_dir == test_dir
    assert rules_mk.subdirs == []
    assert rules_mk.targets == expected_targets

    assert rules_mk.rules[0].variables == []
    assert rules_mk.rules[0].commands == []
    assert rules_mk.rules[0].dependencies == []
    assert rules_mk.rules[0].include_dirs == []
    assert rules_mk.rules[0].target == "TESTX.MODULE"
    assert (
        str(rules_mk)
        == """MODULEs := TESTX.MODULE


TESTX.MODULE_SRC=$(d)/TEST.SQLRPGLE
TESTX.MODULE_DEP=
TESTX.MODULE_RECIPE=SQLRPGLE_TO_MODULE_RECIPE
"""
    )


def test_src_obj_mapping_from_subfolder1():
    # Test loading from a valid file
    test_dir = DATA_PATH / "build_env" / "sample_project1" / "innerdir2"
    rules_mk = RulesMk.from_file(test_dir / "Rules.mk", test_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": [],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": [],
        "SRVPGMs": [],
        "PGMs": ["HELLOP.PGM", "TEST2.PGM"],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }
    assert rules_mk.src_obj_mapping["TEST.SQLRPGLE"] == ["TEST2.PGM"]
    assert rules_mk.containing_dir == test_dir
    assert rules_mk.subdirs == []
    assert rules_mk.targets == expected_targets

    assert rules_mk.rules[0].variables == []
    assert rules_mk.rules[0].commands == []
    assert rules_mk.rules[0].dependencies == []
    assert rules_mk.rules[0].include_dirs == []
    assert rules_mk.rules[0].target == "HELLOP.PGM"
    assert (
        str(rules_mk)
        == """PGMs := HELLOP.PGM TEST2.PGM


HELLOP.PGM_SRC=$(d)/HELLO.PGM.RPGLE
HELLOP.PGM_DEP=
HELLOP.PGM_RECIPE=PGM.RPGLE_TO_PGM_RECIPE
TEST2.PGM_SRC=$(d)/TEST.SQLRPGLE
TEST2.PGM_DEP=
TEST2.PGM_RECIPE=PGM.SQLRPGLE_TO_PGM_RECIPE
"""
    )


def test_pgm_recipe():
    # Test loading from a valid file
    rules_mk = RulesMk.from_file(data_dir / "pgm.rules.mk", data_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": [],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": ["HELLO.MODULE"],
        "SRVPGMs": [],
        "PGMs": ["HELLO.PGM", "HELLOSQL.PGM", "HELLOP.PGM"],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }
    assert rules_mk.containing_dir == data_dir
    assert rules_mk.subdirs == []
    assert rules_mk.targets == expected_targets
    assert rules_mk.rules[0].variables == []
    assert rules_mk.rules[0].commands == []
    assert rules_mk.rules[0].dependencies == []
    assert rules_mk.rules[0].include_dirs == []
    assert rules_mk.rules[0].target == "HELLO.MODULE"
    assert rules_mk.rules[0].source_file == "HELLO.RPGLE"
    assert (
        str(rules_mk.rules[0])
        == """HELLO.MODULE_SRC=HELLO.RPGLE
HELLO.MODULE_DEP=
HELLO.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE\n"""
    )

    assert rules_mk.rules[1].variables == []
    assert rules_mk.rules[1].commands == []
    assert rules_mk.rules[1].dependencies == []
    assert rules_mk.rules[1].include_dirs == []
    assert rules_mk.rules[1].target == "HELLO.PGM"
    assert rules_mk.rules[1].source_file == "HELLO.RPGLE"
    assert (
        str(rules_mk.rules[1])
        == """HELLO.PGM_SRC=HELLO.RPGLE
HELLO.PGM_DEP=
HELLO.PGM_RECIPE=PGM.RPGLE_TO_PGM_RECIPE\n"""
    )

    assert rules_mk.rules[2].variables == []
    assert rules_mk.rules[2].commands == []
    assert rules_mk.rules[2].dependencies == []
    assert rules_mk.rules[2].include_dirs == []
    assert rules_mk.rules[2].target == "HELLOSQL.PGM"
    assert rules_mk.rules[2].source_file == "HELLO.SQLRPGLE"
    assert (
        str(rules_mk.rules[2])
        == """HELLOSQL.PGM_SRC=HELLO.SQLRPGLE
HELLOSQL.PGM_DEP=
HELLOSQL.PGM_RECIPE=PGM.SQLRPGLE_TO_PGM_RECIPE\n"""
    )

    assert rules_mk.rules[3].variables == []
    assert rules_mk.rules[3].commands == []
    assert rules_mk.rules[3].dependencies == []
    assert rules_mk.rules[3].include_dirs == []
    assert rules_mk.rules[3].target == "HELLOP.PGM"
    assert rules_mk.rules[3].source_file == "HELLO.PGM.RPGLE"
    assert (
        str(rules_mk.rules[3])
        == """HELLOP.PGM_SRC=HELLO.PGM.RPGLE
HELLOP.PGM_DEP=
HELLOP.PGM_RECIPE=PGM.RPGLE_TO_PGM_RECIPE\n"""
    )

    assert (
        str(rules_mk)
        == """MODULEs := HELLO.MODULE
PGMs := HELLO.PGM HELLOSQL.PGM HELLOP.PGM\n\n
HELLO.MODULE_SRC=HELLO.RPGLE
HELLO.MODULE_DEP=
HELLO.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE
HELLO.PGM_SRC=HELLO.RPGLE
HELLO.PGM_DEP=
HELLO.PGM_RECIPE=PGM.RPGLE_TO_PGM_RECIPE
HELLOSQL.PGM_SRC=HELLO.SQLRPGLE
HELLOSQL.PGM_DEP=
HELLOSQL.PGM_RECIPE=PGM.SQLRPGLE_TO_PGM_RECIPE
HELLOP.PGM_SRC=HELLO.PGM.RPGLE
HELLOP.PGM_DEP=
HELLOP.PGM_RECIPE=PGM.RPGLE_TO_PGM_RECIPE
"""
    )


def test_relativepath_subfolder1():
    # Test loading from a valid file
    test_dir = DATA_PATH / "build_env" / "sample_project2" / "QRPGLESRC"
    rules_mk = RulesMk.from_file(test_dir / "Rules.mk", test_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": [],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": [],
        "SRVPGMs": [],
        "PGMs": ["HELLO.PGM"],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }
    # assert rules_mk.src_obj_mapping['HELLO.RPGLE'] == ['HELLO.PGM']
    assert rules_mk.containing_dir == test_dir
    assert rules_mk.subdirs == []
    assert rules_mk.targets == expected_targets

    assert rules_mk.rules[0].variables == []
    assert rules_mk.rules[0].commands == []
    assert rules_mk.rules[0].dependencies == []
    assert rules_mk.rules[0].include_dirs == []
    assert rules_mk.rules[0].target == "HELLO.PGM"
    assert (
        str(rules_mk)
        == """PGMs := HELLO.PGM


HELLO.PGM_SRC=hello.rpgle
HELLO.PGM_DEP=
HELLO.PGM_RECIPE=PGM.RPGLE_TO_PGM_RECIPE
"""
    )


def test_relativepath_subfolder2():
    # Test loading from a valid file

    test_dir = DATA_PATH / "build_env" / "sample_project2" / "QTEMP"
    rules_mk = RulesMk.from_file(test_dir / "Rules.mk", test_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": [],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": [],
        "SRVPGMs": [],
        "PGMs": [],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }
    assert rules_mk.containing_dir == test_dir
    assert rules_mk.subdirs == ["QRPGLESRC"]
    assert rules_mk.targets == expected_targets
    assert (
        str(rules_mk)
        == """SUBDIRS := QRPGLESRC



"""
    )


def test_relativepath_subfolder3():
    # Test loading from a valid file

    test_dir = DATA_PATH / "build_env" / "sample_project2" / "QTEMP" / "QRPGLESRC"
    rules_mk = RulesMk.from_file(test_dir / "Rules.mk", test_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": [],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": ["HELLO2.MODULE"],
        "SRVPGMs": [],
        "PGMs": [],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }
    # assert rules_mk.src_obj_mapping['HELLO.RPGLE'] == ['HELLO.PGM']
    assert rules_mk.containing_dir == test_dir
    assert rules_mk.subdirs == []
    assert rules_mk.targets == expected_targets

    assert rules_mk.rules[0].variables == []
    assert rules_mk.rules[0].commands == []
    assert rules_mk.rules[0].dependencies == ['hello.pgm']
    assert rules_mk.rules[0].include_dirs == []
    assert rules_mk.rules[0].target == "HELLO2.MODULE"
    assert (
        str(rules_mk)
        == """MODULEs := HELLO2.MODULE


HELLO2.MODULE_SRC=hello2.rpgle
HELLO2.MODULE_DEP=hello.pgm
HELLO2.MODULE_RECIPE=RPGLE_TO_MODULE_RECIPE
"""
    )


def test_relativepath_rules():
    # Test loading from a valid file

    test_dir = DATA_PATH / "build_env" / "sample_project2"
    rules_mk = RulesMk.from_file(test_dir / "Rules.mk", test_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": [],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": [],
        "SRVPGMs": [],
        "PGMs": [],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }
    assert rules_mk.containing_dir == test_dir
    assert rules_mk.subdirs == [
        "QTEMP/QRPGLESRC",
        "QRPGLESRC",
    ]
    assert rules_mk.targets == expected_targets
    assert (
        str(rules_mk)
        == """SUBDIRS := QTEMP/QRPGLESRC QRPGLESRC



"""
    )


def test_sql_recipe():
    # Test loading from a valid file
    rules_mk = RulesMk.from_file(data_dir / "sql.rules.mk", data_dir)
    expected_targets = {
        "TRGs": [],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": [],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": [],
        "SRVPGMs": ["VALUSE.SRVPGM"],
        "PGMs": [],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": ["VALUSE.QMQRY"],
        "WSCSTs": [],
        "MSGs": [],
    }
    assert rules_mk.containing_dir == data_dir
    assert rules_mk.targets == expected_targets
    assert rules_mk.rules[0].variables == []
    assert rules_mk.rules[0].commands == []
    assert rules_mk.rules[0].dependencies == []
    assert rules_mk.rules[0].include_dirs == []
    assert rules_mk.rules[0].target == "VALUSE.SRVPGM"
    assert rules_mk.rules[0].source_file == "VALUSE.SQLVAR"
    assert (
        str(rules_mk.rules[0])
        == """VALUSE.SRVPGM_SRC=VALUSE.SQLVAR
VALUSE.SRVPGM_DEP=
VALUSE.SRVPGM_RECIPE=SQLVAR_TO_SRVPGM_RECIPE\n"""
    )

    assert rules_mk.rules[1].variables == []
    assert rules_mk.rules[1].commands == []
    assert rules_mk.rules[1].dependencies == []
    assert rules_mk.rules[1].include_dirs == []
    assert rules_mk.rules[1].target == "VALUSE.QMQRY"
    assert rules_mk.rules[1].source_file == "VALUSE.SQL"
    assert (
        str(rules_mk.rules[1])
        == """VALUSE.QMQRY_SRC=VALUSE.SQL
VALUSE.QMQRY_DEP=
VALUSE.QMQRY_RECIPE=SQL_TO_QMQRY_RECIPE\n"""
    )

    assert (
        str(rules_mk)
        == """SRVPGMs := VALUSE.SRVPGM
QMQRYs := VALUSE.QMQRY\n\n
VALUSE.SRVPGM_SRC=VALUSE.SQLVAR
VALUSE.SRVPGM_DEP=
VALUSE.SRVPGM_RECIPE=SQLVAR_TO_SRVPGM_RECIPE
VALUSE.QMQRY_SRC=VALUSE.SQL
VALUSE.QMQRY_DEP=
VALUSE.QMQRY_RECIPE=SQL_TO_QMQRY_RECIPE
"""
    )


def test_trg_recipe():
    # Test loading from a valid file
    rules_mk = RulesMk.from_file(data_dir / "trg.rules.mk", data_dir)
    expected_targets = {
        "TRGs": ["ORD700A.TRG"],
        "DTAARAs": [],
        "DTAQs": [],
        "SQLs": [],
        "BNDDs": [],
        "PFs": ["MYPF1.FILE"],
        "LFs": [],
        "DSPFs": [],
        "PRTFs": [],
        "CMDs": [],
        "MODULEs": [],
        "SRVPGMs": [],
        "PGMs": ["TRGPGM.PGM"],
        "MENUs": [],
        "PNLGRPs": [],
        "QMQRYs": [],
        "WSCSTs": [],
        "MSGs": [],
    }
    assert rules_mk.src_obj_mapping["ORD700A.SYSTRG"] == ["ORD700A.TRG"]
    assert rules_mk.src_obj_mapping["MYPF1.PF"] == ["MYPF1.FILE"]
    assert rules_mk.src_obj_mapping["TRGPGM.PGM.RPGLE"] == ["TRGPGM.PGM"]
    assert rules_mk.containing_dir == data_dir
    assert rules_mk.subdirs == []
    assert rules_mk.targets == expected_targets

    # Test MYPF1.FILE rule
    assert rules_mk.rules[0].variables == []
    assert rules_mk.rules[0].commands == []
    assert rules_mk.rules[0].dependencies == []
    assert rules_mk.rules[0].include_dirs == []
    assert rules_mk.rules[0].target == "MYPF1.FILE"
    assert rules_mk.rules[0].source_file == "mypf1.pf"
    assert (
        str(rules_mk.rules[0])
        == """MYPF1.FILE_SRC=mypf1.pf
MYPF1.FILE_DEP=
MYPF1.FILE_RECIPE=PF_TO_FILE_RECIPE
""")
    # Test TRGPGM.PGM rule
    assert rules_mk.rules[1].variables == []
    assert rules_mk.rules[1].commands == []
    assert rules_mk.rules[1].dependencies == []
    assert rules_mk.rules[1].include_dirs == []
    assert rules_mk.rules[1].target == "TRGPGM.PGM"
    assert rules_mk.rules[1].source_file == "trgpgm.pgm.rpgle"
    assert (
        str(rules_mk.rules[1])
        == """TRGPGM.PGM_SRC=trgpgm.pgm.rpgle
TRGPGM.PGM_DEP=
TRGPGM.PGM_RECIPE=PGM.RPGLE_TO_PGM_RECIPE
""")
    # Test ORD700A.TRG rule
    assert rules_mk.rules[2].variables == []
    assert rules_mk.rules[2].commands == []
    assert rules_mk.rules[2].dependencies == ["TRGPGM.PGM", "MYPF1.FILE"]
    assert rules_mk.rules[2].include_dirs == []
    assert rules_mk.rules[2].target == "ORD700A.TRG"
    assert rules_mk.rules[2].source_file == "ORD700A.SYSTRG"
    assert (
        str(rules_mk.rules[2])
        == """ORD700A.TRG_SRC=ORD700A.SYSTRG
ORD700A.TRG_DEP=TRGPGM.PGM MYPF1.FILE
ORD700A.TRG_RECIPE=SYSTRG_TO_TRG_RECIPE
"""
    )

    # Test full RulesMk string output
    assert (
        str(rules_mk)
        == """TRGs := ORD700A.TRG
PFs := MYPF1.FILE
PGMs := TRGPGM.PGM


MYPF1.FILE_SRC=mypf1.pf
MYPF1.FILE_DEP=
MYPF1.FILE_RECIPE=PF_TO_FILE_RECIPE
TRGPGM.PGM_SRC=trgpgm.pgm.rpgle
TRGPGM.PGM_DEP=
TRGPGM.PGM_RECIPE=PGM.RPGLE_TO_PGM_RECIPE
ORD700A.TRG_SRC=ORD700A.SYSTRG
ORD700A.TRG_DEP=TRGPGM.PGM MYPF1.FILE
ORD700A.TRG_RECIPE=SYSTRG_TO_TRG_RECIPE
""")
