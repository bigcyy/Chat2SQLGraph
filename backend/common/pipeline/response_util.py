import json
import uuid
from enum import Enum

class Status(Enum):
    START = "start"                # 步骤开始执行
    IN_PROGRESS = "in_progress"     # 步骤正在进行
    COMPLETED = "completed"         # 步骤执行完成
    ERROR = "error"                 # 步骤发生错误

def to_stream_chunk_response(chat_id, step_id, data, status: Status, chat_record_id = uuid.uuid1()):
    chunk = json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id),
                        'step_id': str(step_id), 'data': data, 'status': status.value})
    return format_stream_chunk(chunk)

def format_stream_chunk(response_str):
    return 'data: ' + response_str + '\n\n'