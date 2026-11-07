"""Wrapper interactivo para FZF multiplataforma con estética Tokyo Night."""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional
from src.ui.theme import FZF_THEME_ARGS

class FZFSelector:
    def __init__(self):
        self.fzf_path = self._find_fzf()

    def _find_fzf(self) -> Optional[str]:
        which = shutil.which("fzf")
        if which:
            return which

        if sys.platform == "win32":
            home = Path.home()
            local_appdata = os.environ.get("LOCALAPPDATA", "")
            exe_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent.parent
            candidates = [
                exe_dir / "fzf.exe",
                exe_dir / "fzf.EXE",
                home / ".anime" / "fzf.exe",
                home / ".anime" / "fzf.EXE",
                Path(local_appdata) / "Microsoft" / "WinGet" / "Links" / "fzf.exe",
                home / "scoop" / "shims" / "fzf.exe",
                home / "scoop" / "apps" / "fzf" / "current" / "fzf.exe",
            ]
            for c in candidates:
                if c.exists():
                    return str(c)
        return None

    def build_cmd(
        self,
        prompt: str = "  ❯ ",
        height: str = "40%",
        delimiter: str = "\t",
        with_nth: str = "1",
        header: Optional[str] = None
    ) -> List[str]:
        """Construye el comando fzf con bordes redondeados y paleta Tokyo Night."""
        cmd = [
            self.fzf_path or "fzf",
            f"--delimiter={delimiter}",
            f"--with-nth={with_nth}",
            f"--prompt={prompt}",
            f"--height={height}",
        ]
        cmd.extend(FZF_THEME_ARGS)
        if header:
            cmd.append(f"--header={header}")
        return cmd

    def select(
        self,
        options: List[str],
        prompt: str = "  ❯ ",
        height: str = "40%",
        delimiter: str = "\t",
        with_nth: str = "1",
        header: Optional[str] = None
    ) -> Optional[str]:
        """Abre fzf de forma interactiva y retorna la línea seleccionada en UTF-8."""
        if not options:
            return None

        # Si fzf no está instalado, usar selector numérico de consola
        if not self.fzf_path:
            return self._fallback_select(options, prompt, header=header)

        cmd = self.build_cmd(
            prompt=prompt,
            height=height,
            delimiter=delimiter,
            with_nth=with_nth,
            header=header
        )

        # Enviar input en bytes UTF-8 explícitos para no depender del codepage cp1252 de Windows
        input_bytes = "\n".join(options).encode("utf-8")
        try:
            # stdout se captura para obtener la selección
            # stderr se deja en None para que fzf dibuje su interfaz visual directamente en la terminal
            proc = subprocess.run(
                cmd,
                input=input_bytes,
                stdout=subprocess.PIPE,
                stderr=None,
                check=False
            )
            if proc.returncode == 0:
                selected = proc.stdout.decode("utf-8", errors="replace").strip()
                return selected if selected else None
            return None
        except Exception:
            return self._fallback_select(options, prompt, header=header)

    def _fallback_select(
        self,
        options: List[str],
        prompt: str,
        header: Optional[str] = None
    ) -> Optional[str]:
        if header:
            print(f"\n--- {header} ---")
        print(f"\n{prompt}")
        valid_items = []
        for opt in options:
            parts = opt.split("\t")
            if len(parts) > 1 and parts[1] == "HEADER":
                print(f"\n  {parts[0]}")
                continue
            valid_items.append(opt)
            print(f"  [{len(valid_items)}] {parts[0]}")

        print("  [0] Cancelar / Salir\n")
        try:
            choice = input("Elige una opción: ").strip()
            if not choice or choice == "0":
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(valid_items):
                return valid_items[idx]
        except (ValueError, IndexError):
            pass
        return None
