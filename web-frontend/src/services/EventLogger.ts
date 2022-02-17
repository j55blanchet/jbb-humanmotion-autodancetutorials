export interface Event {
  timestamp: Date;
  desc: string;
}

export class EventLogger {

  public readonly logEntries = new Array<Event>();

  public log(logString: string) {
    const time = new Date();
    this.logEntries.push({
      timestamp: time,
      desc: logString,
    });

    console.log(`EVENT ${time.toISOString()}: ${logString}`);
  }

  public retrieveLog() {
    const logFile = this.logEntries.map((entry) => `${entry.timestamp.toISOString()}: ${entry.desc}`).join('\n');
    return logFile;
  }
}

const eventLogger = new EventLogger();
export default eventLogger;
