import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from typing import Callable

from loguru import logger

from database.request import get_orders_on_verify
from handlers.users import on_success_payment, on_failure_payment, on_time_confirm_end
from utils.payments import check_order_status

sched = AsyncIOScheduler()


async def __check_jobs_and_reschedule():
    jobs = sched.get_jobs()
    # job_name = f"{user_id}_{order_id}_{end_time.strftime('%Y%m%d%H%M%S')}"
    for j in jobs:
        logger.info(j.name, j.id)
        if 'pay' in j.name:
            logger.info(j.name, j.id)
            user_id, order_id, end_time = j.name.split('_')[1:]
            status = check_order_status(order_id)
            if status:
                await on_success_payment(user_id, order_id)
                sched.remove_job(job_id=j.id)
            else:
                if datetime.now() >= datetime.strptime(end_time, '%d.%m.%Y %H:%M:%S'):
                    await on_failure_payment(user_id, order_id)
                    sched.remove_job(job_id=j.id)


async def check_active_orders_to_close():
    """status: on_verify"""
    on_verify_orders = await get_orders_on_verify()
    for order in on_verify_orders:
        order_id, _date = order
        if datetime.now().date() > _date:
            await on_time_confirm_end(order_id)

async def global_sched():
    sched.add_job(name='global_sched', id='global_sched', func=__check_jobs_and_reschedule, trigger='interval', seconds=30)
    sched.add_job(name='global_sched', id='global_sched', func=check_active_orders_to_close, trigger='cron', hour=20, minute=0)
    sched.start()
