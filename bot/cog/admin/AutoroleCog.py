import asyncio
import json
import re
import enum
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, TypedDict, Dict, Any, Type, TypeVar, Optional

import discord

from discord.ext import commands

from core.util import make_escape, tryint, predicate_or, pop_dict
from core.util.discord import walk_components
from bot.MyCog import MyCog
from bot.MyModal import MyModal
from bot.error import UserInputWarning
from bot.RawView import RawView

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
AutoroleParamsT = TypeVar("AutoroleParamsT", AutoroleButtonParams, AutoroleDropdownValueParams)


class AutoroleFormBase(MyModal, ABC):
    @property
    @abstractmethod
    def view_type(self) -> AutoroleViewT:
        pass

    # Instance fields
    __slots__ = ("prefill", "content", "roles")
    prefillL: Optional[discord.Message]
    content: discord.ui.TextInput
    roles: discord.ui.TextInput

    # noinspection PyUnusedLocal
    async def parse_content_input(self, interaction: discord.Interaction) -> AutoroleMessageParams:
        content = self.content.value
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

    @abstractmethod
    async def parse_roles_input(self, interaction: discord.Interaction) -> List[AutoroleParamsT]:
        pass

    # noinspection PyUnusedLocal
    async def parse_fields(self, interaction: discord.Interaction) -> Dict[str, Any]:
        return {}

    ROLENAME = "%ROLENAME%"
    _rolename_regex = re.compile(ROLENAME, re.IGNORECASE)
    label_escape, label_unescape, label_rev_escape = map(staticmethod, make_escape(escape="%"))

    @classmethod
    def label_rolename_replace(cls, repl: str, string: str):
        return cls._rolename_regex.sub(repl, string)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            content = await self.parse_content_input(interaction)
        except UserInputWarning:
            raise
        except json.JSONDecodeError as ex:
            raise UserInputWarning(f":x: Error parsing \"Content\" JSON\n```{ex}```") from ex
        except Exception as ex:
            raise UserInputWarning(":x: Error parsing \"Content\" input") from ex

        try:
            roles = await self.parse_roles_input(interaction)
        except UserInputWarning:
            raise
        except json.JSONDecodeError as ex:
            raise UserInputWarning(f":x: Error parsing \"Roles\" JSON\n```{ex}```") from ex
        except Exception as ex:
            raise UserInputWarning(":x: Error parsing \"Roles\" input") from ex

        if len(roles) > 25:
            raise UserInputWarning(":x: Maximum is 25 roles")

        try:
            if not self.prefill:
                await interaction.followup.send(
                    **content,
                    view=self.view_type(roles, **(await self.parse_fields(interaction))),
                    allowed_mentions=discord.AllowedMentions.none(),
                )
            else:
                await self.prefill.edit(
                    **content,
                    view=self.view_type(roles, **(await self.parse_fields(interaction))),
                    allowed_mentions=discord.AllowedMentions.none(),
                )
        except TypeError as ex:
            raise UserInputWarning(":x: Cannot mix \"embed\" and \"embeds\" keys") from ex
        except ValueError as ex:
            raise UserInputWarning(":x: \"embeds\" has a maximum of 10 elements") from ex
        except discord.HTTPException as ex:
            raise UserInputWarning(":x: An error occurred") from ex

    @classmethod
    def prefill_content_from_message(cls, message: discord.Message) -> str:
        content = message.content
        embeds = message.embeds

        if len(embeds) == 0:
            content_ = content or ""
        elif len(embeds) == 1:
            content_ = json.dumps({
                **({"content": content} if content else {}),
                "embed": pop_dict(message.embeds[0].to_dict(), "type"),
            }, ensure_ascii=False, indent=4)
        else:
            content_ = json.dumps({
                **({"content": content} if content else {}),
                "embeds": [pop_dict(e.to_dict(), "type") for e in embeds],
            }, ensure_ascii=False, indent=4)

        return content_

    @classmethod
    @abstractmethod
    def prefill_from_message(cls, message: discord.Message) -> AutoroleFormT:
        pass


class AutoroleButtonsForm(AutoroleFormBase, title="Create Autorole (Buttons)"):
    view_type = AutoroleButtonsView

    def __init__(self, prefill: discord.Message = None, content: str = None, roles: str = None):
        super().__init__()
        self.prefill = prefill
        self.content = discord.ui.TextInput(
            label="Message Content",
            style=discord.TextStyle.long,
            placeholder="Enter a string or JSON\n(See help page for JSON format)",
            required=False,
            default=content,
        )
        self.roles = discord.ui.TextInput(
                label="Roles",
                style=discord.TextStyle.long,
                placeholder="Put a role ID on each line\n(See help page for format)",
                required=True,
                default=roles,
            )
        self.add_item(self.content).add_item(self.roles)

    button_styles: Dict[str | None, discord.enums.ButtonStyle] = {
        **dict.fromkeys(("primary", "blurple", "blue", "purple"), discord.enums.ButtonStyle.primary),
        **dict.fromkeys(("secondary", "grey", "gray", None, "."), discord.enums.ButtonStyle.secondary),
        **dict.fromkeys(("success", "green"), discord.enums.ButtonStyle.success),
        **dict.fromkeys(("danger", "red"), discord.enums.ButtonStyle.danger),
    }

    async def parse_roles_input(self, interaction: discord.Interaction) -> List[AutoroleButtonParams]:
        lst: List[Dict[str, Any]] = json.loads(self.roles.value)
        return list(await asyncio.gather(*[self._parse_role_input(interaction, **dct) for dct in lst]))

    async def _parse_role_input(
            self,
            interaction: discord.Interaction,
            *,
            role: str = None, style: Optional[str] = None, emoji: Optional[str] = None, label: Optional[str] = None,
            **_kwargs
    ) -> AutoroleButtonParams:
        if role is None:
            raise UserInputWarning(":x: Role must be specified")

        abp = AutoroleButtonParams()

        if (role_ := interaction.guild.get_role(int(role))) is None:
            raise UserInputWarning(f':x: Unknown role "{role}"')
        abp["role"] = role_

        try:
            abp["style"] = self.button_styles[style]
        except KeyError as ex:
            raise UserInputWarning(f':x: Unknown button style "{style}"') from ex

        if emoji:
            emoji_ = discord.utils.get(interaction.guild.emojis, name=emoji) \
                     or discord.utils.get(interaction.guild.emojis, id=emoji) \
                     or interaction.client.app.emoji.get(emoji)
            if emoji_ is None:
                raise UserInputWarning(":x: Invalid emoji")
            abp["emoji"] = emoji_

        if (label_ := label or (self.ROLENAME if emoji is None else None)) is not None:
            abp["label"] = self.label_unescape(self.label_rolename_replace(role_.name, self.label_escape(label_)))

        return abp

    @classmethod
    def prefill_from_message(cls, message: discord.Message) -> "AutoroleButtonsForm":
        content_ = cls.prefill_content_from_message(message)

        components: List[discord.Button] = walk_components(message)

        # noinspection PyUnresolvedReferences
        roles = [
            {
                "role": AutoroleButtonsView.custom_id_regex.fullmatch(c.custom_id)[1],
                "style": c.style.name,
                **({"emoji": c.emoji.id or c.emoji.name} if c.emoji else {}),
                **({"label": cls.label_rev_escape(c.label)} if c.label else {})
            }
            for c in components
        ]
        roles_ = json.dumps(roles, ensure_ascii=False, indent=4)

        return cls(message, content_, roles_)


class AutoroleDropdownForm(AutoroleFormBase, title="Create Autorole (Dropdown)"):
    view_type = AutoroleDropdownView

    def __init__(self, prefill: discord.Message = None, content: str = None, roles: str = None,
                 _min: str = "1", _max: str = "1"
                 ):
        super().__init__()
        self.prefill = prefill
        self.content = discord.ui.TextInput(
            label="Message Content",
            style=discord.TextStyle.long,
            placeholder="Enter a string or JSON\n(See help page for JSON format)",
            required=False,
            default=content,
        )
        self.roles = discord.ui.TextInput(
            label="Roles",
            style=discord.TextStyle.long,
            placeholder="Put a role ID on each line\n(See help page for format)",
            required=True,
            default=roles,
        )
        self.min = discord.ui.TextInput(
            label="Min",
            style=discord.TextStyle.short,
            placeholder="(min 0, max 25)",
            required=True,
            min_length=1,
            max_length=2,
            default="1",
        )
        self.max = discord.ui.TextInput(
            label="Max",
            style=discord.TextStyle.short,
            placeholder="(min 0, max 25)",
            required=True,
            min_length=1,
            max_length=2,
            default="1",
        )
        self.add_item(self.content).add_item(self.roles).add_item(self.min).add_item(self.max)

    async def parse_roles_input(self, interaction: discord.Interaction) -> List[AutoroleDropdownValueParams]:
        lst: List[Dict[str, Any]] = json.loads(self.roles.value)
        return list(await asyncio.gather(*[self._parse_role_input(interaction, **dct) for dct in lst]))

    async def _parse_role_input(
            self,
            interaction: discord.Interaction,
            *,
            role: str = None,
            emoji: Optional[str] = None, label: Optional[str] = None, description: Optional[str] = None,
            **_kwargs
    ) -> AutoroleDropdownValueParams:
        if role is None:
            raise UserInputWarning(":x: Role must be specified")

        abp = AutoroleDropdownValueParams()

        if (role_ := interaction.guild.get_role(int(role))) is None:
            raise UserInputWarning(f':x: Unknown role "{role}"')
        abp["role"] = role_

        if emoji:
            emoji_ = discord.utils.get(interaction.guild.emojis, name=emoji) \
                     or discord.utils.get(interaction.guild.emojis, id=emoji) \
                     or interaction.client.app.emoji.get(emoji)
            if emoji_ is None:
                raise UserInputWarning(":x: Invalid emoji")
            abp["emoji"] = emoji_

        label_ = label or self.ROLENAME
        abp["label"] = self.label_unescape(self.label_rolename_replace(role_.name, self.label_escape(label_)))

        if description:
            abp["description"] = \
                self.label_unescape(self.label_rolename_replace(role_.name, self.label_escape(description)))

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

    @classmethod
    def prefill_from_message(cls, message: discord.Message) -> "AutoroleDropdownForm":
        content_ = cls.prefill_content_from_message(message)

        dropdown = discord.utils.get(
            walk_components(message),
            type=discord.ComponentType.select
        )

        roles = [
            {
                "role": AutoroleDropdownView.value_regex.fullmatch(o.value)[1],
                "label": cls.label_rev_escape(o.label),
                **({"emoji": o.emoji.id or o.emoji.name} if o.emoji else {}),
                **({"description": cls.label_rev_escape(o.description)} if o.description else {})
            }
            for o in dropdown.options
        ]
        roles_ = json.dumps(roles, ensure_ascii=False, indent=4)

        min_ = str(dropdown.min_values)
        max_ = str(dropdown.max_values)

        return cls(message, content_, roles_, min_, max_)


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
        raise UserInputWarning(":x: Must be on a valid autorole message")

    autorole_form_cls = (
        AutoroleType.Dropdown
        if discord.utils.get(components, type=discord.enums.ComponentType.select) is not None
        else AutoroleType.Buttons
    ).value
    await ctx.response.send_modal(autorole_form_cls.prefill_from_message(message))
edit_autorole: discord.app_commands.ContextMenu
