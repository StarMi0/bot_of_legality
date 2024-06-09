import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from typing import Callable

from handlers.users import on_success_payment, on_failure_payment
from utils.payments import check_order_status

sched = AsyncIOScheduler()


# class PaymentChecker:
#     def __init__(self, check_order_status: Callable[[str], bool], on_success: Callable[[str, str], None],
#                  on_failure: Callable[[str, str], None]):
#         self.scheduler = AsyncIOScheduler()
#         self.check_order_status = check_order_status
#         self.on_success = on_success
#         self.on_failure = on_failure
#         self.scheduler.start()
#
#     async def check_payment(self, user_id: str, order_id: str):
#         # Имитация асинхронной функции, которая вызывает check_order_status
#         result = await asyncio.to_thread(self.check_order_status, order_id)
#         if result:
#             await self.on_success(user_id, order_id)
#             return True
#         else:
#             return False
#
#     def schedule_check(self, user_id: str, order_id: str):
#         end_time = datetime.now() + timedelta(minutes=15)
#         job_id = f"{user_id}_{order_id}_{end_time.strftime('%Y%m%d%H%M%S')}"
#
#         def check_status_job():
#             asyncio.create_task(self._check_and_reschedule(job_id, user_id, order_id, end_time))
#
#         self.scheduler.add_job(check_status_job, IntervalTrigger(minutes=1), id=job_id)
#
#     async def _check_and_reschedule(self, job_id: str, user_id: str, order_id: str, end_time: datetime):
#         if datetime.now() >= end_time:
#             await self.on_failure(user_id, order_id)
#             self.scheduler.remove_job(job_id)
#         else:
#             success = await self.check_payment(user_id, order_id)
#             if success:
#                 self.scheduler.remove_job(job_id)
#
#     def stop(self):
#         self.scheduler.shutdown()
#
#
# payment_checker = PaymentChecker(check_order_status, on_success_payment, on_failure_payment)


async def __check_jobs_and_reschedule():
    jobs = sched.get_jobs()
    # job_name = f"{user_id}_{order_id}_{end_time.strftime('%Y%m%d%H%M%S')}"
    for j in jobs:
        if 'pay' in j.name:
            user_id, order_id, end_time = j.name.split('_')
            status = check_order_status(order_id)
            if status:
                await on_success_payment(user_id, order_id)
            else:
                if datetime.now() >= datetime.strptime(end_time, '%d.%m.%Y %H:%M:%S'):
                    await on_failure_payment(user_id, order_id)
                    sched.remove_job(job_id=j.id)


async def global_sched():
    sched.add_job(name='global_sched', id='global_sched', func=__check_jobs_and_reschedule, trigger='interval', seconds=30)
    sched.start()