# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for kanging stickers or making new ones. Thanks @rupansh"""

import io
import math
import urllib.request
from os import remove
from PIL import Image
import random
from telethon.tl.types import DocumentAttributeFilename, MessageMediaPhoto
from userbot import bot, CMD_HELP
from userbot.events import register
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetID
from telethon.tl.types import DocumentAttributeSticker

KANGING_STR = [
    "kk eae men. Nice stiker, kibei!",
    "Dando uma de Havoc e kibando...",
    "Fazendo uma armadilha pra\nkibar seu sticker...",
    "Kibando esse sticker, kek...",
    "Opa, ótimo sticker!\nSe importa se eu kibar? kek",
    "hehe acabei de roubar seu sticker\nhehe...",
    "cherry-picking seu sticker, hue...",
    "Rosas são vermelhas, violetas são azuis...\nEnquanto você lê, seu sticker está sendo kibado kek...",
    "Kibando seu sticker...",
    "Que belo sticker, kibei fodase... ",
]


@register(outgoing=True, pattern="^.kibe")
async def kang(args):
    """ Comando .kibe kiba stickers ou cria novos, kek. """
    user = await bot.get_me()
    if not user.username:
        user.username = user.first_name
    message = await args.get_reply_message()
    photo = None
    emojibypass = False
    is_anim = False
    emoji = None

    if message and message.media:
        if isinstance(message.media, MessageMediaPhoto):
            await args.edit(f"`{random.choice(KANGING_STR)}`")
            photo = io.BytesIO()
            photo = await bot.download_media(message.photo, photo)
        elif "image" in message.media.document.mime_type.split('/'):
            await args.edit(f"`{random.choice(KANGING_STR)}`")
            photo = io.BytesIO()
            await bot.download_file(message.media.document, photo)
            if (DocumentAttributeFilename(file_name='sticker.webp') in
                    message.media.document.attributes):
                emoji = message.media.document.attributes[1].alt
                emojibypass = True
        elif "tgsticker" in message.media.document.mime_type:
            await args.edit(f"`{random.choice(KANGING_STR)}`")
            await bot.download_file(message.media.document,
                                    'AnimatedSticker.tgs')

            attributes = message.media.document.attributes
            for attribute in attributes:
                if isinstance(attribute, DocumentAttributeSticker):
                    emoji = attribute.alt

            emojibypass = True
            is_anim = True
            photo = 1
        else:
            await args.edit("`Arquivo não suportado!`")
            return
    else:
        await args.edit("`Lol, não posso kibar isso`")
        return

    if photo:
        splat = args.text.split()
        if not emojibypass:
            emoji = "🤔"
        pack = 1
        if len(splat) == 3:
            pack = splat[2]  # User sent both
            emoji = splat[1]
        elif len(splat) == 2:
            if splat[1].isnumeric():
                # User wants to push into different pack, but is okay with
                # thonk as emote.
                pack = int(splat[1])
            else:
                # User sent just custom emote, wants to push to default
                # pack
                emoji = splat[1]

        packname = f"a{user.id}_by_{user.username}_{pack}"
        packnick = f"Pack de Kibes do @{user.username} vol.{pack}"
        cmd = '/newpack'
        file = io.BytesIO()

        if not is_anim:
            image = await resize_photo(photo)
            file.name = "sticker.png"
            image.save(file, "PNG")
        else:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = '/newanimated'

        response = urllib.request.urlopen(
            urllib.request.Request(f'http://t.me/addstickers/{packname}'))
        htmlstr = response.read().decode("utf8").split('\n')

        if "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>." not in htmlstr:
            async with bot.conversation('Stickers') as conv:
                await conv.send_message('/addsticker')
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packname)
                x = await conv.get_response()
                while "120" in x.text:
                    pack += 1
                    packname = f"a{user.id}_by_{user.username}_{pack}"
                    packnick = f"Pack de Kibes do @{user.username} vol.{pack}"
                    await args.edit("`Mudando para o pack " + str(pack) +
                                    " pois o espaço é insuficiente`")
                    await conv.send_message(packname)
                    x = await conv.get_response()
                    if x.text == "Invalid pack selected.":
                        await conv.send_message(cmd)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.send_message(packnick)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        if is_anim:
                            await conv.send_file('AnimatedSticker.tgs')
                            remove('AnimatedSticker.tgs')
                        else:
                            file.seek(0)
                            await conv.send_file(file, force_document=True)
                        await conv.get_response()
                        await conv.send_message(emoji)
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message("/publish")
                        if is_anim:
                            await conv.get_response()
                            await conv.send_message(f"<{packnick}>")
                        # Ensure user doesn't get spamming notifications
                        await conv.get_response()
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.send_message("/skip")
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message(packname)
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await args.edit(f"`Sticker adicionado em um pacote diferente !\
                            \nO pack acabou de ser criado!\
                            \nPack de kibes [aqui](t.me/addstickers/{packname})",
                                        parse_mode='md')
                        return
                if is_anim:
                    await conv.send_file('AnimatedSticker.tgs')
                    remove('AnimatedSticker.tgs')
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Sorry, the file type is invalid." in rsp.text:
                    await args.edit(
                        "`Falha ao adicionar sticker, use` @Stickers `bot para adicionar o adesivo manualmente.`"
                    )
                    return
                await conv.send_message(emoji)
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message('/done')
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
        else:
            await args.edit("`Preparando um novo pacote de kibes...`")
            async with bot.conversation('Stickers') as conv:
                await conv.send_message(cmd)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packnick)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                if is_anim:
                    await conv.send_file('AnimatedSticker.tgs')
                    remove('AnimatedSticker.tgs')
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Sorry, the file type is invalid." in rsp.text:
                    await args.edit(
                        "`Falha ao adicionar sticker, use` @Stickers `bot para adicionar o adesivo manualmente.`"
                    )
                    return
                await conv.send_message(emoji)
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/publish")
                if is_anim:
                    await conv.get_response()
                    await conv.send_message(f"<{packnick}>")
                # Ensure user doesn't get spamming notifications
                await conv.get_response()
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message("/skip")
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message(packname)
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)

        await args.edit(f"`Sticker kibado, kek!`\
            \nPack de kibe [aqui](t.me/addstickers/{packname})",
                        parse_mode='md')


async def resize_photo(photo):
    """ Redimensione a foto fornecida para 512x512 """
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        image.thumbnail(maxsize)

    return image


@register(outgoing=True, pattern="^.stickerinfo$")
async def get_pack_info(event):
    if not event.is_reply:
        await event.edit("`Não consigo buscar informações do nada, posso ?!`")
        return

    rep_msg = await event.get_reply_message()
    if not rep_msg.document:
        await event.edit("`Responda a um adesivo para obter os detalhes do pacote`")
        return

    try:
        stickerset_attr = rep_msg.document.attributes[1]
        await event.edit(
            "`Buscando detalhes do pacote de adesivos, aguarde ..`")
    except BaseException:
        await event.edit("`Isso não é um adesivo. Responda a um adesivo, corno.`")
        return

    if not isinstance(stickerset_attr, DocumentAttributeSticker):
        await event.edit("`Isso não é um adesivo. Responda a um adesivo, corno.`")
        return

    get_stickerset = await bot(
        GetStickerSetRequest(
            InputStickerSetID(
                id=stickerset_attr.stickerset.id,
                access_hash=stickerset_attr.stickerset.access_hash)))
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)

    OUTPUT = f"**Título do Sticker:** `{get_stickerset.set.title}\n`" \
        f"**Nome encurtado:** `{get_stickerset.set.short_name}`\n" \
        f"**Oficial:** `{get_stickerset.set.official}`\n" \
        f"**Arquivado:** `{get_stickerset.set.archived}`\n" \
        f"**Stickers no pack:** `{len(get_stickerset.packs)}`\n" \
        f"**Emojis no pack:**\n{' '.join(pack_emojis)}"

    await event.edit(OUTPUT)


CMD_HELP.update({
    "stickers":
    ".kibe\
\nComo funciona: Responda .kibe em algum sticker pra kibar no seu pack\
\n\n.kibe [emoji('s)]\
\nComo funciona: Funciona como o .kibe mas você pode escolher um sticker para ele\
\n\n.kibe [numero]\
\nComo funciona: kiba o sticker/imagem para o pack especificado, mas usa 🤔 como emoji.\
\n\n.kibe [emoji('s)] [numero]\
\nComo funciona: Kiba's o sticker/imagem para o pack especificado e usa os emoji(s) que você escolheu.
})
