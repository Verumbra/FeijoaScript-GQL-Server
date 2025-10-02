"""
Copy a .sql file into a running Postgres Docker container and execute it with psql.

Usage examples:
  python run_sql_in_container.py --container fs-datapipeline-ingest-db ^
      --sql "C:\\path\\to\\schema.sql" --db mydb --user postgres --password mypass

  # Extra psql flags, keep file in container, and verbose:
  python run_sql_in_container.py --container fs-datapipeline-ingest-db \
      --sql ./schema.sql --db mydb --user pguser --password env \
      --psql-arg "--set" --psql-arg "lock_timeout=0" --keep --verbose
"""
from __future__ import annotations
import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

def shell_join(parts: List[str]) -> str:
    # Pretty-print command safely (no execution)
    return " ".join(shlex.quote(p) for p in parts)

def run(cmd: List[str], *, env: Optional[dict] = None, verbose: bool = True) -> None:
    if verbose:
        print(f"\n$ {shell_join(cmd)}")
    try:
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"\nCommand failed with exit code {e.returncode}.", file=sys.stderr)
        sys.exit(e.returncode)

def docker_available(verbose: bool) -> None:
    try:
        run(["docker", "--version"], verbose=verbose)
    except SystemExit:
        print("Docker not found on PATH. Install/start Docker and try again.", file=sys.stderr)
        sys.exit(1)

def ensure_container_running(container: str, verbose: bool) -> None:
    # Returns "true"/"false" or errors if container not found
    try:
        res = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", container],
            check=True, capture_output=True, text=True
        )
        running = res.stdout.strip().lower() == "true"
        if not running:
            print(f"Container '{container}' is not running. Start it and retry.", file=sys.stderr)
            sys.exit(2)
    except subprocess.CalledProcessError:
        print(f"Container '{container}' not found. Check the name.", file=sys.stderr)
        sys.exit(3)

def docker_cp(local_sql: Path, container: str, dest_path_in_container: str, verbose: bool) -> None:
    run(["docker", "cp", str(local_sql), f"{container}:{dest_path_in_container}"], verbose=verbose)

def docker_exec_psql(
    container: str,
    user: str,
    db: str,
    password: str,
    sql_path_in_container: str,
    *,
    psql_bin: str = "psql",
    on_error_stop: bool = True,
    single_transaction: bool = True,
    extra_psql_args: Optional[List[str]] = None,
    verbose: bool = True,
) -> None:
    cmd = ["docker", "exec", "-i", "-e", f"PGPASSWORD={password}", container, psql_bin,
           "-U", user, "-d", db]
    if on_error_stop:
        cmd += ["-v", "ON_ERROR_STOP=1"]
    if single_transaction:
        cmd += ["-1"]
    if extra_psql_args:
        cmd += extra_psql_args
    cmd += ["-f", sql_path_in_container]
    run(cmd, verbose=verbose)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a local SQL file inside a Postgres Docker container.")
    parser.add_argument("--container", required=True, help="Docker container name (e.g., fs-datapipeline-ingest-db)")
    parser.add_argument("--sql", required=True, help="Path to local .sql file")
    parser.add_argument("--db", required=True, help="Target database name inside Postgres")
    parser.add_argument("--user", default="postgres", help="Postgres user (default: postgres)")

    # Password handling: pass a literal, or the name 'env' to read PGPASSWORD env var
    parser.add_argument("--password", required=True,
                        help="Postgres password or 'env' to read from PGPASSWORD environment variable")

    parser.add_argument("--dest", default="/tmp/schema.sql",
                        help="Destination path for the SQL file inside the container (default: /tmp/schema.sql)")
    parser.add_argument("--psql-bin", default="psql",
                        help="Path to psql inside container if non-standard (default: psql)")
    parser.add_argument("--no-stop-on-error", action="store_true",
                        help="Do NOT set ON_ERROR_STOP=1 (default is to stop on first error)")
    parser.add_argument("--no-single-tx", action="store_true",
                        help="Do NOT wrap in a single transaction (default is to use -1)")
    parser.add_argument("--psql-arg", action="append",
                        help="Extra psql arguments, repeatable (e.g., --psql-arg --set --psql-arg lock_timeout=0)")
    parser.add_argument("--keep", action="store_true",
                        help="Keep the copied SQL file inside the container (default: remove after run)")
    parser.add_argument("--verbose", action="store_true", help="Print commands before running")
    return parser.parse_args()

def main() -> None:
    args = parse_args()

    # Resolve password
    if args.password.lower() == "env":
        pw = os.getenv("PASSWORD")
        if not pw:
            print("PASSWORD env var not set (and --password=env was provided).", file=sys.stderr)
            sys.exit(4)
    else:
        pw = args.password

    local_sql = Path(args.sql).expanduser().resolve()
    if not local_sql.exists():
        print(f"SQL file not found: {local_sql}", file=sys.stderr)
        sys.exit(5)

    docker_available(args.verbose)
    ensure_container_running(args.container, args.verbose)

    # 1) Copy file into the container
    docker_cp(local_sql, args.container, args.dest, args.verbose)

    # 2) Execute it with psql inside the container
    try:
        docker_exec_psql(
            container=args.container,
            user=args.user,
            db=args.db,
            password=pw,
            sql_path_in_container=args.dest,
            psql_bin=args.psql_bin,
            on_error_stop=not args.no_stop_on_error,
            single_transaction=not args.no_single_tx,
            extra_psql_args=args.psql_arg or [],
            verbose=args.verbose,
        )
    finally:
        # 3) Optionally remove the file from the container
        if not args.keep:
            run(["docker", "exec", args.container, "rm", "-f", args.dest], verbose=args.verbose)

    print("\n✅ SQL applied successfully.")

if __name__ == "__main__":
    main()