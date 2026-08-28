from __future__ import annotations

from html import escape

import streamlit as st

from src.i18n import tr


FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan",
    "Sophia", "Lucas", "Mia", "James", "Isabella", "Henry",
    "Amelia", "Jack", "Charlotte", "Daniel", "Harper", "Alexander",
    "Evelyn", "Benjamin",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller",
    "Davis", "Wilson", "Anderson", "Taylor", "Thomas", "Moore",
    "Jackson", "Martin", "Lee", "Thompson", "White", "Harris",
    "Clark", "Lewis",
]


def fictional_name(user_id: int) -> str:
    """Return a stable fictional name derived only from the numeric user ID."""
    uid = int(user_id)
    first = FIRST_NAMES[(uid * 17 + 3) % len(FIRST_NAMES)]
    last = LAST_NAMES[(uid * 31 + 7) % len(LAST_NAMES)]
    return f"{first} {last}"


def user_label(user_id: int) -> str:
    return f"ID {int(user_id)} · {fictional_name(user_id)}"


def customer_selector(profiles, label: str, key: str) -> int:
    """Select one customer without sending 160k options to the browser."""
    user_ids = profiles["user_id"]
    first_user = int(user_ids.iloc[0])
    requested = st.query_params.get("user_id")
    requested_user = int(requested) if requested and requested.isdigit() else first_user
    if not user_ids.eq(requested_user).any():
        requested_user = first_user

    user_id = int(
        st.number_input(
            label,
            min_value=int(user_ids.min()),
            max_value=int(user_ids.max()),
            value=requested_user,
            step=1,
            key=key,
        )
    )
    if not user_ids.eq(user_id).any():
        st.warning(
            tr(
                "Ese ID no forma parte de la muestra disponible. Ingresá otro cliente.",
                "That ID is not part of the available sample. Enter another customer.",
            )
        )
        st.stop()

    if st.query_params.get("user_id") != str(user_id):
        st.query_params["user_id"] = str(user_id)
    st.caption(f"{fictional_name(user_id)} · {tr('nombre ficticio', 'fictional name')}")
    return user_id


def user_context(user_id: int, detail: str | None = None):
    detail = detail or tr("Cliente seleccionado", "Selected customer")
    st.markdown(
        f"""
        <div class='user-context'>
          <div class='user-context-label'>{escape(detail)}</div>
          <div class='user-context-value'>ID {int(user_id)} · {escape(fictional_name(user_id))}</div>
          <div class='user-context-note'>{escape(tr("Nombre ficticio para visualización", "Fictional name for display"))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
