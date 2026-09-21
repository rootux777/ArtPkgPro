"""Provision DSH via its supported launch-token exchange; secrets never print."""
from __future__ import annotations

import argparse
import base64
import getpass
import json
import os
import re
import tempfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

import artpkg_dsh_bridge as bridge


DIAGNOSTICS = {
    "INVALID_LAUNCH_URL": "Paste only the full launch URL (not Markdown brackets), using the configured loopback address and its current token.",
    "INVALID_LAUNCH_TOKEN": "Paste only the 43-character value after token=, without the URL, quotes, spaces, or Markdown brackets.",
    "AUTH_REJECTED": "DSH returned HTTP 401: the launch token was rejected. Use the current launch URL from the running DSH process.",
    "AUTH_FORBIDDEN": "DSH returned HTTP 403: the host trust policy rejected the request.",
    "AUTH_RESPONSE_INVALID": "DSH did not return the expected authentication redirect and session cookie.",
    "CONFIG_EXISTS": "Configuration already exists. Use --replace-credentials only if you intend to renew authentication.",
    "NO_MODELS": "Authentication succeeded, but DSH returned no selectable models. Configure a model provider in DSH.",
    "MODEL_SELECTION_INVALID": "Enter one of the displayed model numbers.",
    "INPUT_CLOSED": "Terminal input closed before setup finished. Run the setup task in an interactive terminal.",
    "CANCELLED": "Setup was cancelled. No review prompt was sent.",
}
STAGE_HELP = {
    "configuration": "Check the loopback origin and configuration path.",
    "launch-url input": "Enter the current launch URL directly into the hidden terminal prompt and press Enter.",
    "launch-token input": "Enter only the current launch token directly into the hidden terminal prompt and press Enter.",
    "authentication exchange": "Check DSH reachability and the current launch URL. No credentials have been saved.",
    "model catalog": "The launch exchange succeeded, but the authenticated model-catalog request failed. Check the DSH API and provider configuration.",
    "model selection": "Enter a number from the model list.",
    "preset installation": "Check preset-directory permissions and whether a different review guard already exists; it will not be overwritten.",
    "preset verification": "Check that DSH discovers the installed restricted preset and that both preset files match the trusted copies.",
    "configuration save": "Check write access to the configuration directory. Symlink configuration targets are not permitted.",
}


class SetupFailure(bridge.DSHError):
    """Only fixed diagnostic codes may cross the secret-handling boundary."""
    def __init__(self, code: str):
        self.code = code
        super().__init__(DIAGNOSTICS[code])


def report_status(config: Path, stage: str, state: str, code: str = "", hint: str = "") -> None:
    """Best-effort private, atomic status file; no input, exceptions or credentials."""
    temporary = None
    try:
        config.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".dsh-setup-status-", dir=config.parent)
        with os.fdopen(fd, "w") as stream:
            json.dump({"stage": stage, "state": state, "code": code, "hint": hint}, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, config.with_name("dsh-setup-status.json"))
    except OSError:
        pass  # A diagnostic write must not mask the original setup failure.
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except OSError:
                pass


class CaptureExchange(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def token_launch_url(token: str, origin: str) -> str:
    """Build an exchange URL only at the explicitly configured loopback origin."""
    origin = bridge.local_url(origin)
    token = token.strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{43}", token):
        raise SetupFailure("INVALID_LAUNCH_TOKEN")
    return origin + "/?token=" + token


def exchange(launch_url: str, origin: str) -> str:
    """Exchange a user-supplied launch URL, without redirects or proxy leakage."""
    launch_url = launch_url.strip()
    try:
        url = urlsplit(launch_url)
    except ValueError:
        raise SetupFailure("INVALID_LAUNCH_URL") from None
    query = parse_qs(url.query, keep_blank_values=True)
    if (f"{url.scheme}://{url.netloc}" != origin or url.path != "/" or url.fragment
            or set(query) != {"token"} or len(query["token"]) != 1
            or not re.fullmatch(r"[A-Za-z0-9_-]{43}", query["token"][0])):
        raise SetupFailure("INVALID_LAUNCH_URL")
    opener = build_opener(ProxyHandler({}), CaptureExchange())
    try:
        with opener.open(Request(launch_url), timeout=20):
            raise SetupFailure("AUTH_RESPONSE_INVALID")
    except HTTPError as exc:
        try:
            if exc.code == 401:
                raise SetupFailure("AUTH_REJECTED") from None
            if exc.code == 403:
                raise SetupFailure("AUTH_FORBIDDEN") from None
            if exc.code != 303 or exc.headers.get("Location") != "/":
                raise SetupFailure("AUTH_RESPONSE_INVALID") from None
            cookie = exc.headers.get("Set-Cookie", "").split(";", 1)[0]
        finally:
            exc.close()
    authority = url.netloc
    name = "dsh-auth-" + base64.urlsafe_b64encode(bytes.fromhex(bridge.digest(authority.encode()))).decode().rstrip("=")
    if not re.fullmatch(re.escape(name) + r"=v1\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", cookie):
        raise bridge.DSHError("DSH returned an invalid session credential")
    return cookie


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:3080")
    parser.add_argument("--user", required=True, help="Only this authenticated ArtPkg user may use the shared DSH account")
    parser.add_argument("--dsh-home", type=Path, default=Path.home() / ".dsh")
    parser.add_argument("--config", type=Path, default=Path.home() / ".config/artpkg/dsh.json")
    parser.add_argument("--state-root", type=Path, default=Path.home() / ".local/share/artpkg/dsh-review")
    parser.add_argument("--replace-credentials", action="store_true")
    parser.add_argument("--token-only", action="store_true", help="Prompt for just the hidden launch token; build the URL from --base-url")
    args = parser.parse_args()
    os.umask(0o077)
    stage = "configuration"

    def progress(next_stage: str) -> None:
        nonlocal stage
        stage = next_stage
        report_status(args.config, stage, "IN_PROGRESS")
        print(f"Setup stage: {stage}", flush=True)

    try:
        origin = bridge.local_url(args.base_url)
        if args.config.exists() and not args.replace_credentials:
            raise SetupFailure("CONFIG_EXISTS")
        print("DSH review uses a shared DSH account. Only the named ArtPkg user is enabled.")
        if args.token_only:
            print(f"Authentication destination: {origin}", flush=True)
            print("Paste ONLY the value after token= from DSH's launch URL. Input is hidden; press Enter to submit.")
            progress("launch-token input")
            launch_url = token_launch_url(getpass.getpass("DSH launch token (hidden): "), origin)
        else:
            print("Paste the DSH launch URL directly here. Input is hidden and never written to logs or config.")
            progress("launch-url input")
            launch_url = getpass.getpass("DSH launch URL (hidden): ")
        progress("authentication exchange")
        cookie = exchange(launch_url, origin)
        del launch_url
        cfg = {"base_url": origin, "cookie": cookie}
        progress("model catalog")
        catalog = bridge.rpc(cfg, "session/modelCatalog", {})
        routes = [(g["id"], m["id"]) for g in catalog["groups"] for m in g["models"]]
        if not routes:
            raise SetupFailure("NO_MODELS")
        for index, (provider, model) in enumerate(routes, 1):
            print(f"{index}: {provider} / {model}")
        print("The DSH host is local; its model provider may be remote. Verify the provider destination before selecting.")
        progress("model selection")
        try:
            selection = int(input("Model number authorized to receive package text: "))
        except ValueError:
            raise SetupFailure("MODEL_SELECTION_INVALID") from None
        if not 1 <= selection <= len(routes):
            raise SetupFailure("MODEL_SELECTION_INVALID")
        provider, model = routes[selection - 1]
        progress("preset installation")
        deployed = args.dsh_home.resolve() / ".agent-presets" / bridge.PRESET_ID
        deployed.mkdir(mode=0o700, parents=True, exist_ok=True)
        if deployed.is_symlink():
            raise bridge.DSHError("Preset directory cannot be a symbolic link")
        for source, filename in ((bridge.PRESET_FILE, "agent.cordis.yml"), (bridge.GUARD_FILE, bridge.GUARD_FILE.name)):
            target = deployed / filename
            if target.exists() or target.is_symlink():
                if target.is_symlink() or target.read_bytes() != source.read_bytes():
                    raise bridge.DSHError("Refusing to replace a different review preset; restart/fresh-session upgrade required")
            else:
                with target.open("xb") as stream:
                    stream.write(source.read_bytes())
                    stream.flush()
                    os.fsync(stream.fileno())
                target.chmod(0o400)
        args.state_root.mkdir(mode=0o700, parents=True, exist_ok=True)
        cfg.update(provider=provider, model=model, allowed_users=[args.user],
                   state_root=str(args.state_root.absolute()), preset_dir=str(deployed), max_prompt_bytes=262144)
        progress("preset verification")
        bridge.verify_preset(cfg)
        progress("configuration save")
        args.config.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if args.config.is_symlink():
            raise bridge.DSHError("Configuration cannot be a symbolic link")
        fd, name = tempfile.mkstemp(dir=args.config.parent)
        try:
            with os.fdopen(fd, "w") as stream:
                json.dump(cfg, stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, args.config)
        finally:
            if os.path.exists(name):
                os.unlink(name)
        report_status(args.config, "complete", "SUCCEEDED")
        print("DSH authentication, selected model, and restricted preset verified. Configuration saved securely.", flush=True)
        print("Set ARTPKG_DSH_CONFIG_FILE to the configured path in the ArtPkg service and restart it.")
        return 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError, EOFError, KeyboardInterrupt) as exc:
        code = (exc.code if isinstance(exc, SetupFailure) else "INPUT_CLOSED" if isinstance(exc, EOFError)
                else "CANCELLED" if isinstance(exc, KeyboardInterrupt) else "STAGE_FAILED")
        hint = DIAGNOSTICS.get(code, STAGE_HELP[stage])
        report_status(args.config, stage, "FAILED", code, hint)
        print(f"DSH setup failed safely at {stage} [{code}]. {hint} No review prompt was sent.", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())