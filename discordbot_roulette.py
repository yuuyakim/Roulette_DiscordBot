import random
import discord
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from discord.ext import commands, tasks
from keep import keep_alive

load_dotenv()
TOKEN=os.getenv("TOKEN")

# 削除対象のチャンネルを管理するセット
active_delete_channels = set()

intents = discord.Intents.all()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def roulette(ctx, *args):
    print(f'Start roulette {args}!')
    selected_item = select_random(*args)
    await ctx.send(f'Roulette結果: {selected_item}')


async def _delete_old_messages(channel):
    """5分以上前のメッセージを削除し、削除件数を返す"""
    try:
        if not channel:
            print(f'チャンネルが見つかりません')
            return 0
        
        # 5分以前の時刻
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        print(f'[DEBUG] cutoff_time (UTC): {cutoff_time}')
        deleted_count = 0
        
        async for message in channel.history(limit=None, oldest_first=True):
            # メッセージのタイムスタンプを確認
            print(f'[DEBUG] message.created_at: {message.created_at} (type: {type(message.created_at)}, tzinfo: {message.created_at.tzinfo})')
            
            # メッセージがカットオフ時刻以降の場合は終了
            if message.created_at >= cutoff_time:
                print(f'[DEBUG] カットオフ時刻に到達: {message.created_at} >= {cutoff_time}')
                break
            
            # 5分以上前のメッセージを削除
            try:
                await message.delete()
                deleted_count += 1
            except discord.Forbidden:
                print(f'メッセージを削除できません (権限なし): {message.id}')
                break
            except discord.HTTPException as e:
                print(f'メッセージ削除エラー: {e}')
                break
        
        if deleted_count > 0:
            print(f'{deleted_count} 件のメッセージを削除しました')
        return deleted_count
    except Exception as e:
        print(f'削除処理エラー: {e}')
        return 0


@bot.command()
async def start_polling(ctx):
    """現在のチャンネルに対して1分間隔のメッセージ削除ポーリングを開始"""
    channel_id = ctx.channel.id
    print(f'[DEBUG] start_polling: チャンネルID {channel_id}')
    
    if channel_id in active_delete_channels:
        await ctx.send(f'このチャンネルは既に削除ポーリングが動作中です')
        return
    
    # チャンネルIDをアクティブなリストに追加
    active_delete_channels.add(channel_id)
    print(f'[DEBUG] チャンネル登録: {active_delete_channels}')
    await ctx.send(f'このチャンネルの1分間隔削除ポーリングを開始しました')
    
    # 初回削除を即実行
    deleted_count = await _delete_old_messages(ctx.channel)
    await ctx.send(f'初回削除完了: {deleted_count} 件のメッセージを削除しました')


@bot.command()
async def stop_polling(ctx):
    """現在のチャンネルのメッセージ削除ポーリングを停止"""
    channel_id = ctx.channel.id
    
    if channel_id not in active_delete_channels:
        await ctx.send(f'このチャンネルのポーリングは動作していません')
        return
    
    # チャンネルIDをアクティブなリストから削除
    active_delete_channels.discard(channel_id)
    await ctx.send(f'このチャンネルの削除ポーリングを停止しました')


@bot.event
async def on_ready():
    print(f'{bot.user} がログインしました')
    if not delete_old_messages_task.is_running():
        delete_old_messages_task.start()
        print(f'メッセージ削除ポーリングタスクを開始しました')
    else:
        print(f'メッセージ削除ポーリングタスク既に動作中')


@tasks.loop(minutes=1)
async def delete_old_messages_task():
    """1分ごとに全アクティブチャンネルの古いメッセージを削除"""
    print(f'[DEBUG] ポーリング実行: アクティブチャンネル {list(active_delete_channels)}')
    for channel_id in list(active_delete_channels):
        channel = bot.get_channel(channel_id)
        if channel:
            print(f'[DEBUG] チャンネル {channel_id} をスキャン')
            await _delete_old_messages(channel)
        else:
            # チャンネルが見つからない場合は削除
            print(f'[DEBUG] チャンネル {channel_id} が見つかりません')
            active_delete_channels.discard(channel_id)



def select_random(*args):
    # 可変長引数をランダムで1つ選択して返す
    if not args:
        return None  # 引数がない場合は None を返す
    return random.choice(args)

keep_alive()
try:
    bot.run(os.environ['TOKEN'])
except:
    os.system("kill")
bot.run(TOKEN)