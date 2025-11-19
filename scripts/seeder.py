"""
Central seeder runner — load and run individual seeder modules (e.g. user.py).
"""

import logging
import importlib.util
import pathlib
import sys

logger = logging.getLogger("cartify.seeder")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def load_seeder_module(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    project_root = pathlib.Path(__file__).resolve().parent
    repo_root = project_root.parent
    repo_root_str = str(repo_root.resolve())
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
        logger.info("Added repo root to sys.path: %s", repo_root_str)

    user_seeder_path = project_root / "user.py"
    if not user_seeder_path.exists():
        logger.error("User seeder not found at %s", user_seeder_path)
        sys.exit(1)

    user_mod = load_seeder_module(user_seeder_path, "scripts.user")

    seeders = []
    if hasattr(user_mod, "seed") and callable(user_mod.seed):
        seeders.append(("user", user_mod.seed))
    else:
        logger.error("user.py does not expose a callable `seed()` function")
        sys.exit(1)

    for name, seeder_fn in seeders:
        logger.info("Running %s seeder...", name)
        try:
            seeder_fn()
            logger.info("%s seeder completed.", name)
        except Exception:
            logger.exception("Seeder %s failed", name)
            sys.exit(1)


if __name__ == "__main__":
    main()
