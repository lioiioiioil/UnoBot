from threading import Thread
import queue_stream

threadsByChatId = {}
st = queue_stream.stream()
q = Thread(target= st.run)
q.start()
