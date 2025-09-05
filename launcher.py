
import time, traceback, sys
print(">>> Launcher starting...")
try:
    from embassy_bot import main
except Exception as e:
    print("IMPORT FAILURE:", e)
    traceback.print_exc()
    time.sleep(30)  # علشان تلحق تقرا اللوج قبل ما الكونتينر يخرج
    sys.exit(1)

try:
    main()
except Exception as e:
    print("RUNTIME FAILURE:", e)
    traceback.print_exc()
    time.sleep(30)
    sys.exit(1)
