import streamlit as st
import base64
import os
import textwrap
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
import streamlit.components.v1 as components

from database.supabase_client import get_supabase_client


class ProfileCardGenerator:

    @staticmethod
    def load_font(size, bold=False):

        if os.name == "nt":
            path = (
                r"C:\Windows\Fonts\arialbd.ttf"
                if bold
                else r"C:\Windows\Fonts\arial.ttf"
            )

            if os.path.exists(path):
                return ImageFont.truetype(path, size)

        for path in [
            (
                "/usr/share/fonts/truetype/dejavu/"
                "DejaVuSans-Bold.ttf"
                if bold else
                "/usr/share/fonts/truetype/dejavu/"
                "DejaVuSans.ttf"
            ),
            (
                "/usr/share/fonts/truetype/liberation2/"
                "LiberationSans-Bold.ttf"
                if bold else
                "/usr/share/fonts/truetype/liberation2/"
                "LiberationSans-Regular.ttf"
            )
        ]:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)

        return ImageFont.load_default()

    @classmethod
    def create_png(cls, photo_bytes, nickname, username, health_goal=""):

        width, height = 1200, 630

        canvas = Image.new("RGB", (width, height), "#EAF5EE")
        draw = ImageDraw.Draw(canvas)

        draw.rounded_rectangle(
            (30, 30, 1170, 600),
            radius=38,
            fill="#FFFFFF",
            outline="#CDE7D6",
            width=3
        )

        draw.rounded_rectangle(
            (50, 50, 430, 580),
            radius=30,
            fill="#E5F4EA"
        )

        # Create circular avatar.
        size = 270
        x, y = 105, 165

        avatar = None

        if photo_bytes:
            try:
                with Image.open(BytesIO(photo_bytes)) as original:
                    avatar = ImageOps.fit(
                        original.convert("RGB"),
                        (size, size),
                        method=Image.Resampling.LANCZOS
                    )
            except Exception:
                avatar = None

        if avatar is not None:

            mask = Image.new("L", (size, size), 0)

            ImageDraw.Draw(mask).ellipse(
                (0, 0, size - 1, size - 1),
                fill=255
            )

            canvas.paste(avatar, (x, y), mask)

        else:

            draw.ellipse(
                (x, y, x + size, y + size),
                fill="#CDE9D7"
            )

            initial = (nickname.strip() or username or "H")[0].upper()

            draw.text(
                (x + 100, y + 80),
                initial,
                font=cls.load_font(100, bold=True),
                fill="#287A4E"
            )

        draw.ellipse(
            (x, y, x + size, y + size),
            outline="#FFFFFF",
            width=8
        )

        # Profile identity.
        draw.text(
            (480, 130),
            "HEALTHYME",
            font=cls.load_font(28, bold=True),
            fill="#278253"
        )

        name = nickname.strip() or username or "HealthyMe Member"
        lines = textwrap.wrap(name, width=19)[:2]

        text_y = 205

        for line in lines:
            draw.text(
                (480, text_y),
                line,
                font=cls.load_font(48, bold=True),
                fill="#244D37"
            )

            text_y += 65

        draw.text(
            (482, text_y + 10),
            f"@{username}",
            font=cls.load_font(30),
            fill="#728579"
        )

        # Health Goal.
        goal_y = 405

        draw.text(
            (482, goal_y),
            "HEALTH GOAL",
            font=cls.load_font(20, bold=True),
            fill="#278253"
        )

        goal_text = health_goal.strip() or "Not added yet"
        goal_lines = textwrap.wrap(goal_text, width=34)[:2]

        for index, line in enumerate(goal_lines):
            draw.text(
                (482, goal_y + 32 + index * 30),
                line,
                font=cls.load_font(22),
                fill="#526B5B"
            )

        # HealthyMe Member badge.
        draw.rounded_rectangle(
            (480, 535, 800, 587),
            radius=24,
            fill="#E5F4EA"
        )

        draw.text(
            (500, 547),
            "HealthyMe Member",
            font=cls.load_font(22, bold=True),
            fill="#287A4E"
        )

        output = BytesIO()
        canvas.save(output, format="PNG")

        return output.getvalue()


def display_profile():

    st.title("My Profile")
    st.write("Your personal information and health goals.")
    st.divider()

    # -----------------------------
    # CHECK AUTHENTICATED USER
    # -----------------------------

    user_id = st.session_state.get("auth_user_id")

    if not user_id:
        st.error("Please log in again to view your profile.")
        return

    supabase = get_supabase_client()

    # -----------------------------
    # LOAD PROFILE FROM SUPABASE
    # -----------------------------

    if st.session_state.get("profile_loaded_user_id") != user_id:

        try:
            response = (
                supabase.table("users")
                .select(
                    "username, nickname, birthday, "
                    "height, weight, health_goal, avatar_path"
                )
                .eq("auth_user_id", user_id)
                .limit(1)
                .execute()
            )

            profiles = response.data or []

            if not profiles:
                st.error("Your saved profile was not found.")
                return

            profile = profiles[0]

            # Save the profile picture path.
            st.session_state.avatar_path = (
                profile.get("avatar_path") or ""
            )

            st.session_state.username = (
                profile.get("username") or ""
            )

            st.session_state.nickname = (
                profile.get("nickname") or ""
            )

            st.session_state.birthday = (
                profile.get("birthday") or ""
            )

            st.session_state.height = float(
                profile.get("height") or 160.0
            )

            st.session_state.weight = float(
                profile.get("weight") or 50.0
            )

            st.session_state.health_goal = (
                profile.get("health_goal") or ""
            )

            # Update the OOP object if it exists.
            user = st.session_state.get("user")

            if user is not None:
                user.nickname = st.session_state.nickname
                user.birthday = st.session_state.birthday
                user.height = st.session_state.height
                user.weight = st.session_state.weight

            st.session_state.profile_loaded_user_id = user_id

        except Exception as error:
            st.error("Could not load your profile from Supabase.")

            with st.expander("Technical details"):
                st.code(str(error))

            return

    # -----------------------------
    # PROFILE PICTURE
    # -----------------------------

    if "show_profile_photo_uploader" not in st.session_state:
        st.session_state.show_profile_photo_uploader = False

    # Load saved picture once per logged-in user.
    if st.session_state.get("_avatar_loaded_for") != user_id:

        st.session_state.profile_picture_bytes = None

        try:
            # Get the latest avatar path directly from the database.
            response = (
                supabase.table("users")
                .select("avatar_path")
                .eq("auth_user_id", user_id)
                .limit(1)
                .execute()
            )

            profiles = response.data or []

            if not profiles:
                raise RuntimeError(
                    "Your user profile was not found."
                )

            avatar_path = profiles[0].get("avatar_path") or ""
            st.session_state.avatar_path = avatar_path

            if avatar_path:
                photo_bytes = (
                    supabase.storage
                    .from_("avatars")
                    .download(avatar_path)
                )

                st.session_state.profile_picture_bytes = photo_bytes

        except Exception as error:
            st.warning("Unable to load your saved profile picture.")

            with st.expander("Photo loading details"):
                st.code(str(error))

        st.session_state["_avatar_loaded_for"] = user_id

    # -----------------------------
    # PROFILE HEADER
    # -----------------------------

    photo_col, info_col = st.columns([1, 3])

    # LEFT SIDE: Profile picture.
    with photo_col:

        photo = st.session_state.get("profile_picture_bytes")

        if photo:
            image_format = Image.open(BytesIO(photo)).format

            mime_type = (
                "image/png"
                if image_format == "PNG"
                else "image/jpeg"
            )

            encoded_photo = base64.b64encode(
                photo
            ).decode("utf-8")

            components.html(
                f"""
                <div style="
                    width: 140px;
                    height: 140px;
                    overflow: hidden;
                    border-radius: 50%;
                    border: 3px solid #ccebdc;
                ">
                    <img
                        src="data:{mime_type};base64,{encoded_photo}"
                        alt="Profile picture"
                        style="
                            display: block;
                            width: 140px;
                            height: 140px;
                            object-fit: cover;
                            border-radius: 50%;
                        "
                    />
                </div>
                """,
                height=150,
                width=155,
                scrolling=False
            )

        else:
            # Styled by .hm-avatar-placeholder in Ui/style.css.
            st.markdown(
                (
                    '<div class="hm-avatar-placeholder">'
                    '<svg width="56" height="56" viewBox="0 0 24 24" fill="#47A875">'
                    '<path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 '
                    '2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 '
                    '14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 '
                    '11.54L12 21.35z"/>'
                    '</svg></div>'
                ),
                unsafe_allow_html=True
            )

        if st.button(
            "Edit photo",
            icon=":material/edit:",
            key="edit_profile_photo"
        ):
            st.session_state.show_profile_photo_uploader = True

    # RIGHT SIDE: Nickname and username.
    with info_col:

        username = st.session_state.get("username", "")

        nickname = (
            st.session_state.get("nickname", "") or ""
        ).strip()

        display_name = nickname or username

        st.subheader(display_name)
        st.caption(f"@{username}")
        st.write(":material/favorite: HealthyMe member")

    # Show the uploader and an explicit save button.
    if st.session_state.show_profile_photo_uploader:

        uploaded_photo = st.file_uploader(
            "Choose a profile picture",
            type=["png", "jpg", "jpeg"],
            key=f"profile_photo_upload_{user_id}"
        )

        save_col, cancel_col = st.columns(2)

        with save_col:
            save_photo = st.button(
                "Save Photo",
                use_container_width=True,
                key="save_profile_photo"
            )

        with cancel_col:
            cancel_photo = st.button(
                "Cancel",
                use_container_width=True,
                key="cancel_profile_photo"
            )

        if cancel_photo:
            st.session_state.show_profile_photo_uploader = False
            st.rerun()

        if save_photo:

            if uploaded_photo is None:
                st.warning("Please choose a picture first.")

            else:
                try:
                    photo_bytes = uploaded_photo.getvalue()
                    avatar_path = f"{user_id}/avatar"

                    # Upload the image to private Supabase Storage.
                    supabase.storage.from_("avatars").upload(
                        path=avatar_path,
                        file=photo_bytes,
                        file_options={
                            "content-type": uploaded_photo.type,
                            "upsert": "true"
                        }
                    )

                    # Save the path in the user's profile.
                    result = (
                        supabase.table("users")
                        .update({"avatar_path": avatar_path})
                        .eq("auth_user_id", user_id)
                        .select("avatar_path")
                        .execute()
                    )

                    if not result.data:
                        raise RuntimeError(
                            "The photo uploaded, but its path "
                            "was not saved to your profile."
                        )

                    st.session_state.avatar_path = avatar_path
                    st.session_state.profile_picture_bytes = photo_bytes
                    st.session_state["_avatar_loaded_for"] = user_id
                    st.session_state.show_profile_photo_uploader = False
                    st.session_state.photo_save_success = True

                    st.rerun()

                except Exception as error:
                    st.error("Could not save your profile picture.")

                    with st.expander("Technical details"):
                        st.code(str(error))

    if st.session_state.pop("photo_save_success", False):
        st.success(
            "Profile picture saved successfully!",
            icon=":material/check_circle:"
        )

    st.divider()

    # -----------------------------
    # DISPLAY PROFILE INFORMATION
    # -----------------------------

    info_left, goal_right = st.columns(2, gap="large")

    # LEFT: Personal Information.
    with info_left:

        st.subheader(":material/person: Personal Information")

        st.write("**Username**")
        st.write(st.session_state.username)

        st.write(":material/cake: **Birthday**")
        st.write(
            st.session_state.birthday or "Not added yet"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.write(":material/height: **Height**")
            st.write(f"{st.session_state.height:.1f} cm")

        with col2:
            st.write(":material/monitor_weight: **Weight**")
            st.write(f"{st.session_state.weight:.1f} kg")

    # RIGHT: Health Goal.
    with goal_right:

        st.subheader(":material/flag: Health Goal")

        current_goal = st.session_state.health_goal.strip()

        if current_goal:
            st.write(current_goal)
        else:
            st.caption("Not added yet")

    # -----------------------------
    # EDIT PROFILE
    # -----------------------------

    if "editing_profile" not in st.session_state:
        st.session_state.editing_profile = False

    if not st.session_state.editing_profile:

        if st.button(
            "Edit Profile",
            icon=":material/edit:",
            key="edit_profile_button",
            use_container_width=True
        ):

            # Load current values into the edit form.
            st.session_state.edit_nickname = (
                st.session_state.nickname
            )

            st.session_state.edit_birthday = (
                st.session_state.birthday
            )

            st.session_state.edit_height = float(
                st.session_state.height
            )

            st.session_state.edit_weight = float(
                st.session_state.weight
            )

            st.session_state.edit_health_goal = (
                st.session_state.health_goal
            )

            st.session_state.editing_profile = True
            st.rerun()

    else:

        st.divider()
        st.subheader(":material/edit: Edit Your Profile")

        with st.form("edit_profile_form"):

            new_nickname = st.text_input(
                "Nickname (Optional)",
                key="edit_nickname"
            )

            new_birthday = st.text_input(
                "Birthday",
                key="edit_birthday",
                placeholder="Example: January 1, 2000"
            )

            new_height = st.number_input(
                "Height (cm)",
                min_value=1.0,
                max_value=250.0,
                step=0.1,
                key="edit_height"
            )

            new_weight = st.number_input(
                "Weight (kg)",
                min_value=1.0,
                max_value=300.0,
                step=0.1,
                key="edit_weight"
            )

            new_health_goal = st.text_area(
                "Health Goal",
                key="edit_health_goal",
                placeholder="What health goals do you want to achieve?"
            )

            save_clicked = st.form_submit_button(
                "Save Changes",
                icon=":material/save:",
                use_container_width=True
            )

            cancel_clicked = st.form_submit_button(
                "Cancel",
                use_container_width=True
            )

        if cancel_clicked:
            st.session_state.editing_profile = False
            st.rerun()

        if save_clicked:

            try:
                updated_response = (
                    supabase.table("users")
                    .update({
                        "nickname": new_nickname.strip(),
                        "birthday": new_birthday.strip(),
                        "height": float(new_height),
                        "weight": float(new_weight),
                        "health_goal": new_health_goal.strip()
                    })
                    .eq("auth_user_id", user_id)
                    .select(
                        "username, nickname, birthday, "
                        "height, weight, health_goal"
                    )
                    .execute()
                )

                if not updated_response.data:
                    st.error(
                        "No profile was updated. "
                        "Check your Supabase login and RLS permissions."
                    )
                    return

                saved = updated_response.data[0]

                # Update the active Streamlit session.
                st.session_state.username = saved["username"]

                st.session_state.nickname = (
                    saved.get("nickname") or ""
                )

                st.session_state.birthday = (
                    saved.get("birthday") or ""
                )

                st.session_state.height = float(
                    saved.get("height") or new_height
                )

                st.session_state.weight = float(
                    saved.get("weight") or new_weight
                )

                st.session_state.health_goal = (
                    saved.get("health_goal") or ""
                )

                # Update the OOP object.
                user = st.session_state.get("user")

                if user is not None:
                    user.nickname = st.session_state.nickname
                    user.birthday = st.session_state.birthday
                    user.height = st.session_state.height
                    user.weight = st.session_state.weight

                st.session_state.editing_profile = False

                st.success(
                    "Your profile was saved successfully!",
                    icon=":material/check_circle:"
                )

                st.rerun()

            except Exception as error:
                st.error("Could not save your profile.")

                with st.expander("Technical details"):
                    st.code(str(error))

    # -----------------------------
    # COPY PROFILE CARD
    # -----------------------------

    st.divider()
    st.subheader(":material/share: Share Your Profile")

    if st.button(
        "Refresh Profile Card",
        icon=":material/refresh:",
        use_container_width=True,
        key="refresh_profile_card"
    ):
        # Force the profile to load again from Supabase.
        st.session_state.pop("profile_loaded_user_id", None)
        st.rerun()

    st.caption(
        "Copy your HealthyMe profile card as an image."
    )

    # Read the latest profile values directly from Supabase.
    try:
        latest_response = (
            supabase.table("users")
            .select("username, nickname, health_goal, avatar_path")
            .eq("auth_user_id", user_id)
            .limit(1)
            .execute()
        )

        latest_profiles = latest_response.data or []

        if not latest_profiles:
            st.warning("Could not find your saved profile.")
            return

        latest_profile = latest_profiles[0]

        username = latest_profile.get("username") or ""

        nickname = (
            latest_profile.get("nickname") or ""
        ).strip()

        health_goal = (
            latest_profile.get("health_goal") or ""
        ).strip()

        # Use the saved picture already loaded into the session.
        photo_bytes = st.session_state.get(
            "profile_picture_bytes"
        )

        # Generate the card using the latest database values.
        card_png = ProfileCardGenerator.create_png(
            photo_bytes,
            nickname,
            username,
            health_goal
        )

    except Exception as error:
        st.error("Could not refresh your profile card.")

        with st.expander("Technical details"):
            st.code(str(error))

        return

    # Display a preview of the card.
    st.image(
        card_png,
        caption="Your HealthyMe Profile Card"
    )

    # Copy actual PNG image using the browser clipboard.
    encoded_png = base64.b64encode(card_png).decode("ascii")

    # Button styles live in the root-level Ui folder.
    project_root = Path(__file__).resolve().parent.parent
    css_path = project_root / "Ui" / "copy_button.css"

    if css_path.exists():
        copy_css = css_path.read_text(encoding="utf-8")
    else:
        copy_css = ""
        st.warning(f"CSS file not found: {css_path}")

    html_code = f"""
    <style>
        {copy_css}
    </style>

    <button id="copyCard" type="button">
        Copy Profile
    </button>

    <p id="copyStatus" role="status" aria-live="polite"></p>

    <script>
    const button = document.getElementById("copyCard");
    const status = document.getElementById("copyStatus");

    button.addEventListener("click", async () => {{
        try {{
            if (
                !navigator.clipboard ||
                !navigator.clipboard.write ||
                typeof ClipboardItem === "undefined"
            ) {{
                throw new Error("Image clipboard unavailable");
            }}

            const raw = atob("{encoded_png}");
            const bytes = new Uint8Array(raw.length);

            for (let i = 0; i < raw.length; i++) {{
                bytes[i] = raw.charCodeAt(i);
            }}

            const blob = new Blob(
                [bytes],
                {{type: "image/png"}}
            );

            await navigator.clipboard.write([
                new ClipboardItem({{"image/png": blob}})
            ]);

            button.textContent = "✓ Copied!";
            button.classList.add("copied");
            status.textContent =
                "Profile card copied! Paste it into your chat.";

            setTimeout(() => {{
                button.textContent = "Copy Profile";
                button.classList.remove("copied");
            }}, 2500);

        }} catch (error) {{
            status.textContent =
                "Copy unavailable. Please use Download Profile Card.";
        }}
    }});
    </script>
    """

    components.html(html_code, height=110)

    st.download_button(
        "Download Profile Card",
        icon=":material/download:",
        data=card_png,
        file_name="healthyme_profile.png",
        mime="image/png",
        use_container_width=True
    )