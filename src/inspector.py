class RSKInspector:

    def __init__(self, reader):
        self.reader = reader

    def show_metadata(self):

        print("\n" + "=" * 70)
        print("INSTRUMENT")
        print("=" * 70)
        print(self.reader.rsk.instrument)

        print("\n" + "=" * 70)
        print("DEPLOYMENT")
        print("=" * 70)
        print(self.reader.rsk.deployment)

        print("\n" + "=" * 70)
        print("SCHEDULE")
        print("=" * 70)
        print(self.reader.rsk.scheduleInfo)

    def show_channels(self):

        print("\n" + "=" * 70)
        print("CHANNEL NAMES")
        print("=" * 70)

        try:
            print(self.reader.rsk.channelNames)
        except Exception as e:
            print(e)

        print("\n" + "=" * 70)
        print("CHANNELS")
        print("=" * 70)

        for channel in self.reader.rsk.channels:
            print(channel)

    def inspect_processed(self):

        print("\n" + "=" * 70)
        print("PROCESSED CHANNELS")
        print("=" * 70)

        try:
            print(self.reader.rsk.processedChannelNames)
        except Exception as e:
            print(e)

        print("\n" + "=" * 70)
        print("PROCESSED DATA")
        print("=" * 70)

        try:
            print(type(self.reader.rsk.processedData))
            print(len(self.reader.rsk.processedData))
        except Exception as e:
            print(e)

    def inspect_arrays(self):

        print("\n" + "=" * 70)
        print("DATA ARRAYS")
        print("=" * 70)

        try:
            print(self.reader.rsk.dataArrays)
        except Exception as e:
            print(e)

    def run(self):

        self.show_metadata()

        self.show_channels()

        self.inspect_processed()

        self.inspect_arrays()