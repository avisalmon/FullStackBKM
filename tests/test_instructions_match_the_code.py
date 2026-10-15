"""The instructions are only useful if they are true. This cross-checks what the README, docs and
skills TELL a newcomer to run against what actually exists: scripts, manage.py commands and their
flags, environment variables, gotcha numbers, skill names, workflow inputs.

A stranger follows these literally. A command that does not exist, a flag that was renamed, or a
variable nobody documented is exactly where they get stuck."""

import importlib.util
import re
from pathlib import Path

import pytest
from django.core.management import get_commands, load_command_class

ROOT = Path(__file__).resolve().parent.parent

READ = [ROOT / "README.md", ROOT / "CLAUDE.md", ROOT / "index.html"]
READ += sorted((ROOT / "docs").rglob("*.md"))
READ += sorted((ROOT / ".claude" / "skills").rglob("*.md"))
READ += sorted((ROOT / "tutorial").glob("*.html"))
TEXT = {p: p.read_text(encoding="utf-8") for p in READ}
ALL = "\n".join(TEXT.values())

SKILLS = {p.parent.name for p in (ROOT / ".claude" / "skills").glob("*/SKILL.md")}


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --- scripts ----------------------------------------------------------------------------


def test_every_script_the_docs_mention_exists():
    missing = {
        name
        for name in re.findall(r"scripts/([A-Za-z0-9_]+\.py)", ALL)
        if not (ROOT / "scripts" / name).exists()
    }
    assert not missing, missing


SCRIPT_FLAGS_FROM_SOURCE = ["verify_site", "init_site", "sync_skills", "render_api"]


@pytest.mark.parametrize("script", SCRIPT_FLAGS_FROM_SOURCE)
def test_flags_the_docs_give_to_a_script_exist(script):
    source = (ROOT / "scripts" / f"{script}.py").read_text(encoding="utf-8")
    defined = set(re.findall(r"\"(--[a-z][a-z-]*)\"", source))
    bad = []
    for path, text in TEXT.items():
        for line in re.findall(rf"{script}\.py([^\n`<]*)", text):
            for flag in re.findall(r"(?<![\w-])(--[a-z][a-z-]*)", line):
                if flag not in defined:
                    bad.append(f"{path.name}: {script}.py {flag}")
    assert not bad, bad


def test_render_api_subcommands_in_the_docs_exist():
    parser = load(ROOT / "scripts" / "render_api.py").build_parser()
    real = set(parser._subparsers._group_actions[0].choices)
    used = set(re.findall(r"render_api\.py\s+([a-z][a-z-]+)", ALL))
    assert used <= real, f"docs use render_api.py subcommands that do not exist: {used - real}"


# --- manage.py ----------------------------------------------------------------------------


def test_every_manage_py_command_the_docs_mention_exists():
    real = set(get_commands())
    used = set(re.findall(r"manage\.py\s+([a-z][a-z_]+)", ALL))
    assert used <= real, f"docs mention manage.py commands that do not exist: {used - real}"


def test_flags_the_docs_give_to_our_commands_exist():
    ours = {"backup_db", "report_costs", "bootstrap_site"}
    bad = []
    for name in ours:
        command = load_command_class(get_commands()[name], name)
        known = set(command.create_parser("manage.py", name)._option_string_actions)
        for path, text in TEXT.items():
            for line in re.findall(rf"manage\.py\s+{name}([^\n`<]*)", text):
                for flag in re.findall(r"(?<![\w-])(--[a-z][a-z-]*)", line):
                    if flag not in known:
                        bad.append(f"{path.name}: manage.py {name} {flag}")
    assert not bad, bad


# --- configuration ------------------------------------------------------------------------


def settings_env_names():
    source = (ROOT / "mysite" / "settings.py").read_text(encoding="utf-8")
    names = set(re.findall(r"environ\.get\(\s*\"([A-Z0-9_]+)\"", source))
    names |= set(re.findall(r"env_(?:bool|list)\(\s*\"([A-Z0-9_]+)\"", source))
    return names


def test_every_environment_variable_the_settings_read_is_documented():
    documented = (ROOT / "docs" / "procedures" / "env_vars.md").read_text(encoding="utf-8")
    documented += (ROOT / ".env.example").read_text(encoding="utf-8")
    # RENDER_EXTERNAL_HOSTNAME is set by Render itself; DEBUG-style flags are covered by name.
    missing = {n for n in settings_env_names() if n not in documented}
    assert not missing, f"read in settings.py but not in env_vars.md / .env.example: {missing}"


def test_every_variable_in_render_yaml_is_documented():
    yaml = (ROOT / "render.yaml").read_text(encoding="utf-8")
    keys = set(re.findall(r"- key: ([A-Z0-9_]+)", yaml))
    documented = (ROOT / "docs" / "procedures" / "env_vars.md").read_text(encoding="utf-8")
    assert {k for k in keys if k not in documented} == set()


def test_every_variable_the_scripts_and_commands_read_is_documented():
    documented = (ROOT / "docs" / "procedures" / "env_vars.md").read_text(encoding="utf-8")
    documented += (ROOT / ".env.example").read_text(encoding="utf-8")
    missing = set()
    for path in [*(ROOT / "core").rglob("*.py"), *(ROOT / "scripts").glob("*.py")]:
        for name in re.findall(
            r"environ\.get\(\s*\"([A-Z0-9_]+)\"", path.read_text(encoding="utf-8")
        ):
            if name not in documented:
                missing.add(f"{path.name}: {name}")
    assert not missing, missing


# --- cross-references ---------------------------------------------------------------------


def test_every_gotcha_number_referenced_exists():
    table = (ROOT / "docs" / "procedures" / "gotchas.md").read_text(encoding="utf-8")
    existing = {int(n) for n in re.findall(r"^\| (\d+) \|", table, flags=re.M)}
    sources = ALL + "\n".join(
        p.read_text(encoding="utf-8") for p in [*ROOT.glob("*/*.py"), *ROOT.glob("*/*/*.py")]
        if "env" not in p.parts
    )  # fmt: skip
    used = {int(n) for n in re.findall(r"(?:gotchas?\s*#|gotcha\s+#)(\d+)", sources, flags=re.I)}
    assert used <= existing, f"references to gotchas that do not exist: {used - existing}"


def test_every_skill_named_in_backticks_is_real():
    named = set(re.findall(r"`([a-z]+(?:-[a-z]+)+)`\s+skill", ALL))
    assert named <= SKILLS, f"docs name skills that do not exist: {named - SKILLS}"


def test_every_doc_path_in_backticks_exists():
    bad = set()
    for path, text in TEXT.items():
        for ref in re.findall(r"`((?:docs|tutorial|scripts)/[A-Za-z0-9_./-]+\.[a-z]{2,4})`", text):
            if "<" in ref or "*" in ref:
                continue
            if not (ROOT / ref).exists():
                bad.add(f"{path.name}: {ref}")
    assert not bad, sorted(bad)


def test_workflow_commands_in_the_docs_match_the_workflow_inputs():
    workflow = (ROOT / ".github" / "workflows" / "scheduled-tasks.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch" in workflow and "task:" in workflow
    tasks = set(re.findall(r"scheduled-tasks\.yml\s+-f\s+task=([a-z]+)", ALL))
    from core.views import TASKS

    assert tasks <= set(TASKS), f"docs run workflow tasks that do not exist: {tasks - set(TASKS)}"


def test_the_checklist_phases_all_have_a_skill_or_procedure():
    checklist = (ROOT / "docs" / "new_site_checklist.md").read_text(encoding="utf-8")
    for doc in re.findall(r"\]\((procedures/[a-z_]+\.md)\)", checklist):
        assert (ROOT / "docs" / doc).exists(), doc


def test_the_setup_guide_covers_the_whole_path_from_zero_to_the_chat():
    """docs/get_started.md is the one part a human does alone: it must not lose a step."""
    guide = (ROOT / "docs" / "get_started.md").read_text(encoding="utf-8")
    for needed in (
        "github.com/signup", "two-factor", "git --version", "code.visualstudio.com",
        "GitHub Copilot", "Agent", "Claude Code", "type `hello`", "what is a \"terminal\"?",
        "Terminal -> New Terminal", "the prompt", "git clone https://github.com/avisalmon/FullStackBKM.git",
        "C:\\sites", "trust the authors", "Tell me what to do", "OneDrive",
    ):  # fmt: skip
        assert needed in guide, f"get_started.md lost: {needed}"
    # it promises the chat installs the rest, so the skill that does that must exist
    assert "installs the rest" in guide and "setup-my-computer" in SKILLS


def test_every_entry_sentence_is_a_trigger_of_the_main_skill():
    """Whatever the page and README tell a newcomer to type must start the journey."""
    skill = (ROOT / ".claude" / "skills" / "build-my-site" / "SKILL.md").read_text(encoding="utf-8")
    head = skill.split("---")[1].lower()
    for sentence in (
        "tell me what to do",
        "help me build my full stack site",
        "what's next",
        "continue",
    ):
        assert sentence in head, f"build-my-site does not trigger on: {sentence}"
    claude_md = (ROOT / "CLAUDE.md").read_text(encoding="utf-8").lower()
    assert "tell me what to do" in claude_md, "CLAUDE.md must route the first sentence to the skill"


def test_the_assistant_installs_python_so_the_owner_does_not():
    skill = (ROOT / ".claude" / "skills" / "setup-my-computer" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    for needed in ("winget install", "--scope user", "checksum", "time-box", "Microsoft Store"):
        assert needed.lower() in skill.lower(), needed
