import uuid

from config import session, HazardousPdfTask


# 入库
def save_mysql(entry_id, g_no, flag=None, file_name=None, ddate=None):
    task = session.query(HazardousPdfTask).filter(HazardousPdfTask.entry_id==entry_id)\
        .filter(HazardousPdfTask.g_no == g_no).first()

    if not task:
        task = HazardousPdfTask(id=str(uuid.uuid4()), entry_id=entry_id, g_no=g_no, ddate=ddate)
        session.add(task)
        session.commit()

    if flag:
        if file_name == 'declaration.pdf':
            task.declaration_status = flag
        if file_name == 'label.pdf':
            task.label_status = flag
        if file_name == 'instruction.pdf':
            task.instruction_status = flag

        session.commit()
        return


def judge_is_exist(entry_id, g_no):
    task = session.query(HazardousPdfTask).filter(HazardousPdfTask.entry_id == entry_id)\
        .filter(HazardousPdfTask.g_no == g_no).first()
    return bool(task)
