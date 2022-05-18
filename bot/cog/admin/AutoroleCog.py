import json
import re
import enum
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, TypedDict, Dict, Any, Pattern, Type, TypeVar

import discord

from discord.ext import commands

from core.util import make_escape, tryint, predicate_or
from bot.MyCog import MyCog
from bot.error import UserInputWarning
from bot.RawView import RawView
from core.util.discord import walk_components

if TYPE_CHECKING:
    import discord.types.interactions
    # noinspection PyUnresolvedReferences
    from ...MyBot import MyBot


class AutoroleMessageParams(TypedDict, total=False):
    content: str
    embed: discord.Embed
    embeds: List[discord.Embed]


class AutoroleButtonParams(TypedDict, total=False):
    role: discord.Role
    style: discord.enums.ButtonStyle
    emoji: discord.PartialEmoji | discord.Emoji | str
    label: str


class AutoroleDropdownValueParams(TypedDict, total=False):
    role: discord.Role
    emoji: discord.PartialEmoji | discord.Emoji | str
    label: str
    description: str


class AutoroleButtonsView(RawView):
    custom_id_regex = re.compile(r'autorole:(\d*):.*', re.ASCII)

    def __init__(self, roles_param: List[AutoroleButtonParams]):
        super().__init__()
        for i, p in enumerate(roles_param):
            self.add_item(discord.ui.Button(
                custom_id=f'autorole:{p["role"].id}:{i}',
                **{k: v for k, v in p.items() if k in {"style", "emoji", "label"}},
            ))

    @classmethod
    def interaction_filter(cls, component_type: discord.enums.ComponentType, custom_id: str) -> bool:
        return custom_id.startswith("autorole:")

    @classmethod
    async def dispatch(
            cls,
            component_type: discord.enums.ComponentType,
            custom_id: str,
            interaction: discord.Interaction
    ):
        await interaction.response.defer()
        role_id = tryint(cls.custom_id_regex.fullmatch(custom_id)[1])
        if role_id is not None and (role := interaction.guild.get_role(role_id)) is not None:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role, reason="Autorole")
            else:
                await interaction.user.add_roles(role, reason="Autorole")


class AutoroleDropdownView(RawView):
    custom_id = "autorole_dropdown:"
    value_regex = re.compile(r'(\d*):.*', re.ASCII)

    def __init__(self, roles_param: List[AutoroleDropdownValueParams], min_values: int, max_values: int):
        if max_values > len(roles_param):
            raise UserInputWarning(":x: Max must be less than or equal to number of roles")
        super().__init__()
        self.add_item(discord.ui.Select(
            placeholder="Select a role" if max_values == 1 else "Select roles",
            custom_id=self.custom_id,
            min_values=min_values,
            max_values=max_values,
            options=[discord.components.SelectOption(
                value=f"{p['role'].id}:{i}",
                **{k: v for k, v in p.items() if k in {"label", "description", "emoji"}},
            ) for i, p in enumerate(roles_param)]
        ))

    @classmethod
    def interaction_filter(cls, component_type: discord.enums.ComponentType, custom_id: str) -> bool:
        return custom_id == cls.custom_id

    @classmethod
    async def dispatch(
            cls,
            component_type: discord.enums.ComponentType,
            custom_id: str,
            interaction: discord.Interaction
    ):
        await interaction.response.defer()
        dropdown_component = discord.utils.get(walk_components(interaction.message), custom_id=cls.custom_id)
        data: discord.types.interactions.SelectMessageComponentInteractionData = interaction.data
        user_roles = {discord.Object(r_.id) for r_ in interaction.user.roles}
        all_roles = {
            discord.Object(r)
            for r in (tryint(cls.value_regex.fullmatch(o.value)[1]) for o in dropdown_component.options)
            if r is not None
        }
        roles = {
            discord.Object(r)
            for r in (tryint(cls.value_regex.fullmatch(v)[1]) for v in data["values"])
            if r is not None
        }
        await interaction.user.add_roles(
            *(roles - user_roles),
            reason="Autorole"
        )
        await interaction.user.remove_roles(
            *(user_roles & (all_roles - roles)),
            reason="Autorole"
        )


AutoroleViewT = TypeVar("AutoroleViewT", Type[AutoroleButtonsView], Type[AutoroleDropdownView])
AutoroleFormT = TypeVar("AutoroleFormT", Type["AutoroleButtonsForm"], Type["AutoroleDropdownForm"])


class AutoroleFormBase(discord.ui.Modal, ABC):
    @property
    @abstractmethod
    def view_type(self) -> AutoroleViewT:
        pass

    @property
    @abstractmethod
    def content(self) -> discord.ui.TextInput:
        pass

    @classmethod
    async def parse_content_input(cls, content: str) -> AutoroleMessageParams:
        if not content.startswith("{"):
            return AutoroleMessageParams(content=content)
        else:
            dct: Dict[str, Any] = json.loads(content)
            dct = {k: v for k, v in dct.items() if k in ("content", "embed", "embeds")}
            if "embed" in dct:
                dct["embed"] = discord.Embed.from_dict(dct["embed"])
            if "embeds" in dct:
                dct["embeds"] = [discord.Embed.from_dict(e) for e in dct["embeds"]]
            return AutoroleMessageParams(**dct)

    @property
    @abstractmethod
    def roles(self) -> discord.ui.TextInput:
        pass

    @property
    @abstractmethod
    def roles_regex(self) -> Pattern:
        pass

    @classmethod
    @abstractmethod
    async def parse_roles_input(
            cls,
            interaction: discord.Interaction,
            **kwargs
    ) -> AutoroleButtonParams | AutoroleDropdownValueParams:
        pass

    # noinspection PyUnusedLocal
    async def parse_fields(self, interaction: discord.Interaction) -> Dict[str, Any]:
        return {}

    ROLENAME = "%ROLENAME%"
    label_escape, label_unescape, label_rev_escape = make_escape("%")
    label_rolename_replace = re.compile(ROLENAME, re.IGNORECASE)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            content_ = await self.parse_content_input(self.content.value)
        except Exception as ex:
            raise UserInputWarning(":x: Error parsing \"Content\" input") from ex

        if self.roles_regex.fullmatch(self.roles.value) is None:
            raise UserInputWarning(":x: Invalid \"Roles\" input")
        roles = [
            await self.parse_roles_input(interaction, **m.groupdict())
            for m in map(self.roles_regex.fullmatch, self.roles.value.split("\n")) if m is not None
        ]
        if len(roles) > 25:
            raise UserInputWarning(":x: Maximum is 25 roles")

        try:
            if not self.prefill:
                await interaction.followup.send(
                    **content_,
                    view=self.view_type(roles, **(await self.parse_fields(interaction))),
                    allowed_mentions=discord.AllowedMentions.none(),
                )
            else:
                await self.prefill.edit(
                    **content_,
                    view=self.view_type(roles, **(await self.parse_fields(interaction))),
                    allowed_mentions=discord.AllowedMentions.none(),
                )
        except TypeError as ex:
            raise UserInputWarning(":x: Cannot mix \"embed\" and \"embeds\" keys") from ex
        except ValueError as ex:
            raise UserInputWarning(":x: \"embeds\" has a maximum of 10 elements") from ex
        except discord.HTTPException as ex:
            if "Invalid emoji" in ex.text:
                raise UserInputWarning(":x: Invalid emoji") from ex
            raise UserInputWarning(":x: An error occurred") from ex

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        match error:
            case UserInputWarning(message):
                if not interaction.response.is_done:
                    await interaction.response.send_message(message, ephemeral=True)
                else:
                    await interaction.followup.send(message, ephemeral=True)
            case _:
                if interaction.client.app.config.Debug.DEBUG:
                    await super().on_error(interaction, error)
                if not interaction.response.is_done:
                    await interaction.response.defer()

    prefill: discord.Message = None

    @classmethod
    def prefill_content_from_message(cls, message: discord.Message) -> str:
        content = message.content
        embeds = message.embeds

        if len(embeds) == 0:
            content_ = content or ""
        elif len(embeds) == 1:
            content_ = json.dumps({
                **({"content": content} if content else {}),
                "embed": message.embeds[0].to_dict(),
            }, indent=4)
        else:
            content_ = json.dumps({
                **({"content": content} if content else {}),
                "embeds": [e.to_dict() for e in embeds],
            }, indent=4)

        return content_

    @classmethod
    @abstractmethod
    def prefill_from_message(cls, message: discord.Message) -> AutoroleFormT:
        pass


class AutoroleButtonsForm(AutoroleFormBase, title="Create Autorole (Buttons)"):
    view_type = AutoroleButtonsView

    content = discord.ui.TextInput(
        label="Message Content",
        style=discord.TextStyle.long,
        placeholder="Enter a string or JSON\n(See help page for JSON format)",
        required=False,
    )

    roles = discord.ui.TextInput(
        label="Roles",
        style=discord.TextStyle.long,
        placeholder="Put a role ID on each line\n(See help page for format)",
        required=True,
    )
    roles_regex = re.compile(
        r"""
            ^(?:
                (?P<role>\d{15,20})
                (?:[ ]
                    (?P<style>[\w\.]+)?
                    (?:\:(?P<emoji>[^\s\:]+)\:)?
                    (?<![ ])
                    (?:[ ]
                        (?P<label>.+)
                    )?
                )?
                (?:\n+|$)
            )+
        """, re.ASCII | re.IGNORECASE | re.VERBOSE)

    button_styles: Dict[str | None, discord.enums.ButtonStyle] = {
        **dict.fromkeys(("primary", "blurple", "blue", "purple"), discord.enums.ButtonStyle.primary),
        **dict.fromkeys(("secondary", "grey", "gray", None, "."), discord.enums.ButtonStyle.secondary),
        **dict.fromkeys(("success", "green"), discord.enums.ButtonStyle.success),
        **dict.fromkeys(("danger", "red"), discord.enums.ButtonStyle.danger),
    }

    # noinspection PyMethodOverriding
    @classmethod
    async def parse_roles_input(
        cls,
        interaction: discord.Interaction,
        role: str, style: str | None, emoji: str | None, label: str | None, **kwargs
    ) -> AutoroleButtonParams:
        abp = AutoroleButtonParams()

        if (role_ := interaction.guild.get_role(int(role))) is None:
            raise UserInputWarning(f':x: Unknown role "{role}"')
        abp["role"] = role_

        try:
            abp["style"] = cls.button_styles[style]
        except KeyError as ex:
            raise UserInputWarning(f':x: Unknown button style "{style}"') from ex

        if emoji is not None:
            emoji_ = discord.utils.get(interaction.guild.emojis, name=emoji) \
                     or discord.utils.get(interaction.guild.emojis, id=emoji) \
                     or interaction.client.app.emoji.get(emoji)
            if emoji_ is None:
                raise UserInputWarning(":x: Invalid emoji")
            abp["emoji"] = emoji_

        if (label_ := label if label is not None else (cls.ROLENAME if emoji is None else None)) is not None:
            abp["label"] = cls.label_unescape(cls.label_rolename_replace.sub(role_.name, cls.label_escape(label_)))

        return abp

    # noinspection PyPep8Naming
    @classmethod
    def prefill_class(cls, message: discord.Message, content: str, roles: str) -> "AutoroleButtonsForm":
        content_payload = AutoroleButtonsForm.content.to_component_dict()
        content_payload["value"] = content
        content_ = discord.ui.TextInput.from_component(discord.components.TextInput(content_payload))

        roles_payload = AutoroleButtonsForm.roles.to_component_dict()
        roles_payload["value"] = roles
        roles_ = discord.ui.TextInput.from_component(discord.components.TextInput(roles_payload))

        class _Prefilled_AutoroleButtonsForm(cls):
            prefill = message
            content = content_
            roles = roles_

        return _Prefilled_AutoroleButtonsForm()

    @classmethod
    def prefill_from_message(cls, message: discord.Message) -> "AutoroleButtonsForm":
        content_ = cls.prefill_content_from_message(message)

        components: List[discord.Button] = walk_components(message)
        # noinspection PyUnresolvedReferences
        roles_ = "\n".join([
            f"{AutoroleButtonsView.custom_id_regex.fullmatch(c.custom_id)[1]}"
            f" {c.style.name}{f':{c.emoji.id or c.emoji.name}:' if c.emoji is not None else ''}"
            f"{f' {cls.label_rev_escape(c.label)}' if c.label else ''}"
            for c in components
        ])

        return cls.prefill_class(message, content_, roles_)


class AutoroleDropdownForm(AutoroleFormBase, title="Create Autorole (Dropdown)"):
    view_type = AutoroleDropdownView

    content = discord.ui.TextInput(
        label="Message Content",
        style=discord.TextStyle.long,
        placeholder="Enter a string or JSON\n(See help page for JSON format)",
        required=False,
    )

    roles = discord.ui.TextInput(
        label="Roles",
        style=discord.TextStyle.long,
        placeholder="Put a role ID on each line\n(See help page for format)",
        required=True,
    )
    roles_regex = re.compile(
        r"""
            ^(?:
                (?P<role>\d{15,20})
                (?:[ ]
                    (?:\:(?P<emoji>[^\s\:]+)\:|\.)
                    (?:[ ]
                        (?P<label>.+)
                    )?
                )?
                (?:\n+|$)
            )+
        """, re.ASCII | re.IGNORECASE | re.VERBOSE)

    DESC = "%DESC%"

    min = discord.ui.TextInput(
        label="Min",
        style=discord.TextStyle.short,
        placeholder="(min 0, max 25)",
        required=True,
        min_length=1,
        max_length=2,
        default="1",
    )

    max = discord.ui.TextInput(
        label="Max",
        style=discord.TextStyle.short,
        placeholder="(min 0, max 25)",
        required=True,
        min_length=1,
        max_length=2,
        default="1",
    )

    # noinspection PyMethodOverriding
    @classmethod
    async def parse_roles_input(
        cls,
        interaction: discord.Interaction,
        role: str, emoji: str | None, label: str | None, **kwargs
    ) -> AutoroleDropdownValueParams:
        abp = AutoroleDropdownValueParams()

        if (role_ := interaction.guild.get_role(int(role))) is None:
            raise UserInputWarning(f':x: Unknown role "{role}"')
        abp["role"] = role_

        if emoji is not None:
            emoji_ = discord.utils.get(interaction.guild.emojis, name=emoji) \
                     or discord.utils.get(interaction.guild.emojis, id=emoji) \
                     or interaction.client.app.emoji.get(emoji)
            if emoji_ is None:
                raise UserInputWarning(":x: Invalid emoji")
            abp["emoji"] = emoji_

        if label is not None:
            label_, description, *_ = (*cls.label_escape(label).split(cls.DESC, 1), None)
            if label_ == "":
                label_ = cls.ROLENAME
        else:
            label_ = cls.ROLENAME
            description = None

        abp["label"] = cls.label_unescape(cls.label_rolename_replace.sub(role_.name, label_))
        if description is not None:
            abp["description"] = cls.label_unescape(cls.label_rolename_replace.sub(role_.name, description))

        return abp

    async def parse_fields(self, interaction: discord.Interaction) -> Dict[str, Any]:
        try:
            min_values = int(self.min.value)
            max_values = int(self.max.value)
            min_values, max_values = min(min_values, max_values), max(min_values, max_values)
            if min_values < 0 or max_values > 25:
                raise ValueError("Min & max must be in the range [0, 25]")
        except ValueError as ex:
            raise UserInputWarning(":x: Min & max must be integers in between 0 and 25 (inclusive)") from ex
        if max_values == 0:
            raise UserInputWarning(":x: Max must be greater than 0")
        return {
            "min_values": min_values,
            "max_values": max_values,
        }

    # noinspection PyPep8Naming
    @classmethod
    def prefill_class(
            cls,
            message: discord.Message,
            content: str, roles: str, min_: str, max_: str
    ) -> "AutoroleDropdownForm":
        content_payload = AutoroleDropdownForm.content.to_component_dict()
        content_payload["value"] = content
        content_ = discord.ui.TextInput.from_component(discord.components.TextInput(content_payload))

        roles_payload = AutoroleDropdownForm.roles.to_component_dict()
        roles_payload["value"] = roles
        roles_ = discord.ui.TextInput.from_component(discord.components.TextInput(roles_payload))

        min_payload = AutoroleDropdownForm.min.to_component_dict()
        min_payload["value"] = min_
        min_field = discord.ui.TextInput.from_component(discord.components.TextInput(min_payload))

        max_payload = AutoroleDropdownForm.max.to_component_dict()
        max_payload["value"] = max_
        max_field = discord.ui.TextInput.from_component(discord.components.TextInput(max_payload))

        class _Prefilled_AutoroleDropdownForm(cls):
            prefill = message
            content = content_
            roles = roles_
            min = min_field
            max = max_field

        return _Prefilled_AutoroleDropdownForm()

    @classmethod
    def prefill_from_message(cls, message: discord.Message) -> "AutoroleDropdownForm":
        content_ = cls.prefill_content_from_message(message)

        dropdown = discord.utils.get(
            walk_components(message),
            type=discord.ComponentType.select
        )

        roles_ = "\n".join([
            f"{AutoroleDropdownView.value_regex.fullmatch(o.value)[1]}"
            f" {f':{o.emoji.id or o.emoji.name}:' if o.emoji is not None else '.'}"
            f" {cls.label_rev_escape(o.label)}"
            f"{f'{AutoroleDropdownForm.DESC}{cls.label_rev_escape(o.description)}' if o.description else ''}"
            for o in dropdown.options
        ])

        min_ = str(dropdown.min_values)
        max_ = str(dropdown.max_values)

        return cls.prefill_class(message, content_, roles_, min_, max_)


class AutoroleType(enum.Enum):
    Buttons = AutoroleButtonsForm
    Dropdown = AutoroleDropdownForm


class AutoroleCog(MyCog["MyBot"], commands.Cog):
    @discord.app_commands.command(description="Create an autorole message")
    @discord.app_commands.rename(type_="type")
    @discord.app_commands.describe(type_="Component type")
    @discord.app_commands.guild_only()
    @discord.app_commands.default_permissions(administrator=True)
    async def autorole(self, ctx: discord.Interaction, type_: AutoroleType):
        await ctx.response.send_modal(type_.value())


@discord.app_commands.context_menu(name="Edit Autorole")
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def edit_autorole(ctx: discord.Interaction, message: discord.Message):
    components = walk_components(message)
    if discord.utils.find(
            lambda c: predicate_or(
                AutoroleButtonsView.interaction_filter,
                AutoroleDropdownView.interaction_filter
            )(c.type, c.custom_id),
            components
    ) is None:
        # raise UserInputWarning(":x: Must be on a valid autorole message")
        # TODO command tree context menu error
        await ctx.response.send_message(":x: Must be on a valid autorole message", ephemeral=True)
        return

    type_ = \
        AutoroleType.Dropdown \
        if discord.utils.get(components, type=discord.enums.ComponentType.select) is not None \
        else AutoroleType.Buttons
    await ctx.response.send_modal(type_.value.prefill_from_message(message))
edit_autorole: discord.app_commands.ContextMenu
