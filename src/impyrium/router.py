_consumers = {}

def reset():
    """Clears all subscriptions
    """
    global _consumers
    _consumers = {}

def removeConsumer(ids, consumer):
    """Delete a consumer
    """
    global _consumers
    if type(ids) != list:
        ids = [ids]
    for id in ids:
        if id in _consumers:
            for i in  range(len(_consumers[id])):
                consumer, priority = _consumers[id][i]
                if consumer == consumer:
                    del _consumers[id][i]
                    break


def addConsumer(ids, consumer, priority=0):
    """Adds a new consumer

    Args:
        ids (list<Any>): List of all IDs to recieve.
        consumer (Consumer): The consumer to link
        priority (int): Higher is more priority.
    """
    if type(ids) != list:
        ids = [ids]
    for i in ids:
        if (not i in _consumers):
            _consumers[i] = []
        inserted = False
        for x in range(len(_consumers[i])):
            if priority > _consumers[i][x][1]:
                _consumers[i].insert(x, (consumer, priority))
                inserted = True
                break
        if not inserted:
            _consumers[i].append((consumer, priority))

def sendMessage(msg, id=None):
    """Sends a message

    Args:
        msg (Any): The message to send
        id (Any): The id to send to
    """
    usingId = id
    if id is None:
        if type(msg) == dict:
            if 'msgId' in msg:
                usingId = msg['msgId']
        else:
            usingId = msg.msgId
    if usingId is None:
        return

    sent = False
    if (usingId in _consumers.keys()):
        for c in _consumers[usingId]:
            # If there is no consume function, assume callable
            if 'consume' in dir(c[0]):
                c[0].consume(msg)
            else:
                c[0](msg)
            sent = True
    return sent

def send(id, msg):
    return sendMessage(msg, id)
