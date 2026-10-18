"""Tests for the dhamaan command. Every command runs in process; nothing touches the network."""
import json, os, sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dhamaan import cli
from sim.r2 import base, replay

ROOT = os.path.join(os.path.dirname(__file__), "..")


def run(capsys, *argv):
    code = cli.main(list(argv)); out = capsys.readouterr().out
    return code, out


def test_check_table_on_the_repository_table(capsys):
    code, out = run(capsys, "check-table", "--strict")
    assert code == 0 and "0 errors" in out and "reviewed warnings" in out


def test_check_table_rejects_a_broken_table(capsys, tmp_path):
    p = tmp_path / "t.csv"; p.write_text("id,family\nA01,x\n", encoding="utf-8")
    code, out = run(capsys, "check-table", str(p))
    assert code == 1 and "missing columns" in out


def test_check_case_on_the_repository_case(capsys):
    code, out = run(capsys, "check-case", "--quiet")
    assert code == 0 and out.startswith("0 errors")
    assert run(capsys, "check-case", "--quiet", "--strict")[0] == 1      # flags remain while evidence is open


def test_render_writes_dot(capsys, tmp_path):
    code, out = run(capsys, "render", "--out", str(tmp_path / "d"))
    assert code == 0 and (tmp_path / "d.dot").read_text(encoding="utf-8").startswith("digraph GSN")


def test_new_case_from_template(capsys, tmp_path):
    tdir = tmp_path / "templates"; tdir.mkdir()
    (tdir / "demo.yaml").write_text(open(os.path.join(ROOT, "assurance", "library_robot_case.yaml"), encoding="utf-8").read(), encoding="utf-8")
    code, out = run(capsys, "new-case", "--list", "--templates", str(tdir))
    assert code == 0 and out.strip() == "demo"
    out_file = tmp_path / "c.yaml"
    code, out = run(capsys, "new-case", "demo", "--out", str(out_file), "--title", "My robot", "--templates", str(tdir))
    assert code == 0 and '  title: "My robot"' in out_file.read_text(encoding="utf-8") and "0 errors" in out
    assert run(capsys, "new-case", "demo", "--out", str(out_file), "--templates", str(tdir))[0] == 1     # no silent overwrite
    assert run(capsys, "new-case", "nope", "--out", str(tmp_path / "x.yaml"), "--templates", str(tdir))[0] == 1


def write_log(tmp_path, kind="nominal", size=0.0):
    g, o = replay.standin(base.rng(4242, "CLI", "log", 0))
    g = replay.inject(g, kind, size, 30.0, base.rng(4242, "CLI", "fault", 0))
    (tmp_path / "gnss.csv").write_text(replay.to_csv(g, replay.GNSS_COLUMNS + replay.REF_COLUMNS), encoding="utf-8")
    (tmp_path / "odometry.csv").write_text(replay.to_csv(o, replay.ODO_COLUMNS), encoding="utf-8")
    return str(tmp_path / "gnss.csv"), str(tmp_path / "odometry.csv")


def test_score_log_reports_a_declared_fault(capsys, tmp_path):
    g, o = write_log(tmp_path, "jump", 20.0)
    code, out = run(capsys, "score-log", "--gnss", g, "--odometry", o, "--json")
    res = json.loads(out)
    assert code == 0 and res["reason"] in ("gate", "cusum") and res["t_alarm"] >= 30.0 and "assumed, proposal" in res["note"]


def test_score_log_rejects_a_bad_log(capsys, tmp_path):
    (tmp_path / "g.csv").write_text("t_s,x_m\n0,0\n", encoding="utf-8")
    (tmp_path / "o.csv").write_text("t_s,v_mps,yaw_rad\n0,0,0\n", encoding="utf-8")
    code, out = run(capsys, "score-log", "--gnss", str(tmp_path / "g.csv"), "--odometry", str(tmp_path / "o.csv"))
    assert code == 1 and "log rejected" in out


def test_usage_error_exits_with_two():
    with pytest.raises(SystemExit) as e: cli.main([])
    assert e.value.code == 2
