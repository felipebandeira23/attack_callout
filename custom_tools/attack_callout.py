"""
attack_callout.py

Comando !ataque — apenas Comandante pode usar.
Envia mensagem de admin para TODOS os jogadores do mesmo time.
Compatível com hll_rcon_tool 11.6.1+.
"""

from __future__ import annotations
from datetime import datetime
from typing import Final
from rcon.rcon import Rcon, StructuredLogLineWithMetaData
from rcon.types import Roles

# -------- CONFIG --------
ENABLE_ON_SERVERS: Final = ["1"]
CHAT_COMMANDS: Final = ["!ataque", "!attack", "!atk"]
COOLDOWN_SECONDS: Final = 60
MESSAGE_TEXT: Final = (
    "| ATAQUE COORDENADO | "
    "Foquem em atacar o PRÓXIMO PONTO! "
    "Usem smoke e avancem juntos. Isso é uma ordem!"
)
NOTIFY_CMD_FEEDBACK: Final = True
# ------------------------

_last_used: dict[str, datetime] = {}


def _now() -> datetime:
    return datetime.utcnow()


def _can_use(team: str) -> bool:
    last = _last_used.get(team)
    return True if not last else (_now() - last).total_seconds() >= COOLDOWN_SECONDS


def _set_used(team: str):
    _last_used[team] = _now()


def _is_enabled_on_server() -> bool:
    from rcon.utils import get_server_number
    return str(get_server_number()) in ENABLE_ON_SERVERS


def _norm(s: str | None) -> str:
    return (s or "").strip().lower()


def _get_sender_info(rcon: Rcon, player_id: str) -> tuple[str | None, str | None]:
    role = None
    team = None
    try:
        detailed = rcon.get_detailed_players() or {}
        players = detailed.get("players", {}) or {}
        me = players.get(player_id)
        if me:
            role = me.get("role")
            team = me.get("team")
    except Exception:
        pass

    if not role or not team:
        try:
            info = rcon.get_player_info(player=player_id) or {}
            role = role or info.get("role")
            team = team or info.get("team")
        except Exception:
            pass
    return role, team


def _list_players_same_team(rcon: Rcon, team: str) -> list[str]:
    ids: list[str] = []
    try:
        detailed = rcon.get_detailed_players() or {}
        for pid, p in (detailed.get("players") or {}).items():
            if _norm(p.get("team")) == _norm(team):
                ids.append(pid)
    except Exception:
        pass
    return ids


def _message_many(rcon: Rcon, ids: list[str], msg: str):
    if not ids:
        return
    try:
        rcon.bulk_message_players(ids, [msg] * len(ids))
        return
    except Exception:
        pass
    for pid in ids:
        try:
            rcon.message_player(player_id=pid, message=msg, save_message=False)
        except Exception:
            continue


def handle_attack_on_chat(rcon: Rcon, struct_log: StructuredLogLineWithMetaData):
    if not _is_enabled_on_server():
        return

    msg = (struct_log.get("sub_content") or "").strip().lower()
    if not any(msg.startswith(cmd) for cmd in CHAT_COMMANDS):
        return

    player_id = struct_log.get("player_id_1")
    player_name = struct_log.get("player_name_1") or str(player_id or "unknown")
    if not player_id:
        return

    role, team = _get_sender_info(rcon, player_id)
    if _norm(role) != _norm(Roles.commander.value):  # "armycommander"
        try:
            rcon.message_player(player_id=player_id,
                                message="Apenas o comandante pode usar !ataque.",
                                save_message=False)
        except Exception:
            pass
        return

    if not team:
        try:
            rcon.message_player(player_id=player_id,
                                message="[BOT] Não consegui identificar seu time.",
                                save_message=False)
        except Exception:
            pass
        return

    if not _can_use(team):
        try:
            rcon.message_player(player_id=player_id,
                                message=f"Aguarde {COOLDOWN_SECONDS}s entre usos de !ataque.",
                                save_message=False)
        except Exception:
            pass
        return

    # Envia mensagem a todos do time
    ids = _list_players_same_team(rcon, team)
    _message_many(rcon, ids, f"{MESSAGE_TEXT} (Comandante: {player_name})")

    # Confirmação ao comandante
    if NOTIFY_CMD_FEEDBACK:
        try:
            rcon.message_player(player_id=player_id,
                                message=f"Ordem de ATAQUE enviada a {len(ids)} jogadores do seu time.",
                                save_message=False)
        except Exception:
            pass

    _set_used(team)
