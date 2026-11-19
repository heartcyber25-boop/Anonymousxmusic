# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of ROSE MUSIC


import asyncio
from pathlib import Path

from pyrogram import errors, filters, types

from anony import app, db, lang, logger


broadcasting = asyncio.Lock()

@app.on_message(filters.command(["broadcast"]) & app.sudoers)
@lang.language()
async def _broadcast(_, message: types.Message):
    if not message.reply_to_message:
        return await message.reply_text(message.lang["gcast_usage"])

    if broadcasting.locked():
        return await message.reply_text(message.lang["gcast_active"])

    msg = message.reply_to_message
    copy = "-copy" in message.command
    count, ucount = 0, 0
    groups, users = set(), set()
    sent = await message.reply_text(message.lang["gcast_start"])

    if "-nochat" not in message.command:
        groups = set(await db.get_chats())
    if "-user" in message.command:
        users = set(await db.get_users())

    chats = list(groups | users)
    failed = None
    failed_path = Path(f"broadcast_errors_{message.id}.txt")

    async with broadcasting:
        for chat in chats:
            try:
                if copy:
                    await msg.copy(chat, reply_markup=msg.reply_markup)
                else:
                    await msg.forward(chat)
                if chat in groups:
                    count += 1
                else:
                    ucount += 1
                await asyncio.sleep(0.2)
            except errors.FloodWait as fw:
                logger.warning("Broadcast FloodWait for %s: sleeping %ss", chat, fw.value)
                await asyncio.sleep(fw.value + 2)
                try:
                    if copy:
                        await msg.copy(chat, reply_markup=msg.reply_markup)
                    else:
                        await msg.forward(chat)
                    if chat in groups:
                        count += 1
                    else:
                        ucount += 1
                except Exception as retry_ex:
                    logger.warning("Broadcast retry failed for %s: %s", chat, retry_ex)
                    if not failed:
                        failed = failed_path.open("w", encoding="utf-8")
                    failed.write(f"{chat} - retry: {retry_ex}\n")
            except Exception as ex:
                logger.warning("Broadcast failed for %s: %s", chat, ex)
                if not failed:
                    failed = failed_path.open("w", encoding="utf-8")
                failed.write(f"{chat} - {ex}\n")
                continue

    text = message.lang["gcast_end"].format(count, ucount)
    if failed:
        failed.close()
        await message.reply_document(
            document=str(failed_path),
            caption=text,
        )
        try:
            failed_path.unlink()
        except OSError:
            pass

    await sent.edit_text(text)
