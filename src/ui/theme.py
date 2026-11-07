"""Constantes de estilo y paleta Tokyo Night para Anime-CMD."""

# 24-bit TrueColor ANSI (Paleta Tokyo Night)
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

CYAN = "\033[38;2;125;207;255m"      # #7dcfff (Primario / Prompts / Pointers)
PURPLE = "\033[38;2;187;154;247m"    # #bb9af7 (Acentos / Títulos)
BLUE = "\033[38;2;122;162;247m"      # #7aa2f7 (Info / Subtítulos / Links)
ORANGE = "\033[38;2;255;158;100m"    # #ff9e64 (Warning / Matches fzf)
GREEN = "\033[38;2;158;206;106m"     # #9ece6a (Success / Latino badge)
RED = "\033[38;2;247;118;142m"       # #f7768e (Error)
GRAY = "\033[38;2;86;95;137m"        # #565f89 (Bordes / Muted)
WHITE = "\033[38;2;192;202;245m"     # #c0caf5 (Texto principal / Foreground)
DARK_BG = "\033[48;2;31;35;53m"      # #1f2335 (Fondo de selección fzf)

# Badges visuales estilizados con colores ANSI
TAG_LATINO = f"{GREEN}[LAT]{RESET}"
TAG_CASTELLANO = f"{BLUE}[CAST]{RESET}"
TAG_SUB = f"{ORANGE}[SUB]{RESET}"

# Colores de identidad de cada proveedor
PROVIDER_COLORS = {
    "animeonline": "\033[38;2;255;158;100m",  # Naranja / Ámbar
    "tioanime": "\033[38;2;187;154;247m",     # Magenta / Púrpura
    "jkanime": "\033[38;2;125;207;255m",      # Cyan / Celeste
    "monoschinos": "\033[38;2;224;175;104m",  # Amarillo / Dorado
    "secret": "\033[38;2;247;118;142m",       # Rosa / Neón
}

# Argumentos estándar para FZF con estética moderna y redondeada
FZF_THEME_ARGS = [
    "--ansi",
    "--border=rounded",
    "--layout=reverse",
    "--padding=1,2",
    "--info=inline",
    "--cycle",
    "--highlight-line",
    "--pointer=▶ ",
    "--marker=✓ ",
    "--bind=down:down,up:up,tab:down,btab:up,shift-tab:up,ctrl-j:down,ctrl-k:up,ctrl-n:down,ctrl-p:up",
    "--color=fg:#c0caf5,bg:-1,hl:#ff9e64,fg+:#ffffff,bg+:#2d3f76,hl+:#7aa2f7,pointer:#7dcfff,info:#7aa2f7,prompt:#bb9af7,header:#9ece6a,border:#565f89"
]
