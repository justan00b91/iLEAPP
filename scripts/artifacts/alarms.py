import plistlib
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline


def get_alarms(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []

    for file_found in files_found:
        with open(file_found, "rb") as plist_file:
            pl = plistlib.load(plist_file)

            if 'MTAlarms' in pl:
                if 'MTAlarms' in pl['MTAlarms']:
                    for alarms in pl['MTAlarms']['MTAlarms']:
                        alarms_dict = alarms['$MTAlarm']

                        alarm_title = alarms_dict.get('MTAlarmTitle', 'Alarm')
                        fire_date = alarms_dict.get('MTAlarmFireDate', '')
                        
                        alarm_hour = alarms_dict.get('MTAlarmHour', '')
                        alarm_min = alarms_dict.get('MTAlarmMinute', '')
                        alarm_time = str(alarm_hour).zfill(2)+":"+str(alarm_min).zfill(2)
                        
                        dismiss_date = alarms_dict.get('MTAlarmDismissDate', '')
                        repeat_schedule = decode_repeat_schedule(alarms_dict['MTAlarmRepeatSchedule'])

                        data_list.append((  "Alarm", 
                                            alarm_title, 
                                            alarms_dict['MTAlarmEnabled'], 
                                            alarm_time,
                                            fire_date,
                                            dismiss_date,
                                            alarms_dict['MTAlarmLastModifiedDate'], ', '.join(repeat_schedule),
                                            alarms_dict['MTAlarmSound']['$MTSound']['MTSoundToneID'],
                                            alarms_dict['MTAlarmIsSleep'], 
                                            alarms_dict['MTAlarmBedtimeDoNotDisturb'],
                                            ''
                                        ))

                if 'MTSleepAlarm' in pl['MTAlarms']:
                    for sleep_alarms in pl['MTAlarms']['MTSleepAlarm']:
                        sleep_alarm_dict = pl['MTAlarms']['MTSleepAlarm'][sleep_alarms]

                        alarm_title = sleep_alarm_dict.get('MTAlarmTitle', 'Bedtime')

                        repeat_schedule = decode_repeat_schedule(sleep_alarm_dict['MTAlarmRepeatSchedule'])

                        data_list.append((  "Sleep Alarm", 
                                            alarm_title, 
                                            sleep_alarm_dict['MTAlarmEnabled'],
                                            sleep_alarm_dict['MTAlarmFireDate'],
                                            sleep_alarm_dict['MTAlarmDismissDate'], 
                                            sleep_alarm_dict['MTAlarmLastModifiedDate'],', '.join(repeat_schedule),
                                            sleep_alarm_dict['MTAlarmSound']['$MTSound']['MTSoundToneID'],
                                            sleep_alarm_dict['MTAlarmIsSleep'], 
                                            sleep_alarm_dict['MTAlarmBedtimeDoNotDisturb'],
                                            sleep_alarm_dict['MTAlarmBedtimeFireDate']
                                        ))

            if 'MTStopwatches' in pl:
                if 'MTStopwatches' in pl['MTStopwatches']:
                    for stop_watch in pl['MTStopwatches']['MTStopwatches']:
                        stop_watches_dict = stop_watch['$MTStopwatch']
                        stop_watch_time = stop_watches_dict.get('MTStopwatchCurrentInterval', 0)
                        stop_watch_state = stop_watches_dict.get('MTStopwatchState', '')
                        stop_watch_lapses = stop_watches_dict.get('MTStopwatchLaps', [])
                        stop_watch_lapses.append(stop_watch_time)
                        stop_watch_total_time = sum(stop_watch_lapses)
                        stop_watch_lap_count = len(stop_watch_lapses)
                        
                        data_list.append((  "StopWatch",
                                            "Total Time",
                                            stop_watch_state,
                                            str(datetime.timedelta(seconds = stop_watch_total_time)),
                                            '',
                                            '',
                                            '',
                                            '',
                                            '',
                                            '',
                                            '',
                                            '',
                                        ))

                        for index, val in enumerate(stop_watch_lapses[::-1]):
                            data_list.append((  "StopWatch",
                                                "Lap " + str(stop_watch_lap_count - index),
                                                stop_watch_state,
                                                str(datetime.timedelta(seconds = val)),
                                                '',
                                                '',
                                                '',
                                                '',
                                                '',
                                                '',
                                                '',
                                                ''
                                            ))

            if 'MTTimers' in pl:
                if 'MTTimers' in pl['MTTimers']:
                    for timers in pl['MTTimers']['MTTimers']:
                        timers_dict = timers['$MTTimer']
                        timer_title = timers_dict.get('MTTimerTitle', '')
                        timer_time = timers_dict.get('MTTimerDuration', '')
                        timer_state = timers_dict.get('MTTimerState', '')
                        timer_duration = timers_dict.get('MTTimerDuration', '')
                        dismiss_date = alarms_dict.get('MTAlarmDismissDate', '')
                        repeat_schedule = decode_repeat_schedule(alarms_dict['MTAlarmRepeatSchedule'])

                        data_list.append((  "Timer",
                                            timer_title,
                                            timer_state,
                                            str(datetime.timedelta(seconds = timer_duration)),
                                            '',
                                            '',
                                            timers_dict.get('MTTimerLastModifiedDate',''),
                                            '',
                                            timers_dict['MTTimerSound']['$MTSound']['MTSoundToneID'],
                                            '',
                                            '',
                                            ''
                                        ))

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Alarms')
        report.start_artifact_report(report_folder, 'Alarms')
        report.add_script()
        data_headers = ('Type', 'Title', 'Enabled', 'Time', 'Fire Date', 'Dismiss Date', 'Last Modified', 'Repeat Schedule', 'Sound', 'Is Sleep', 'Bedtime Not Disturbed', 'Bedtime Fire Date')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Alarms'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Alarms'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Alarms found')


def decode_repeat_schedule(repeat_schedule_value):
    days_list = {64: 'Sunday', 32: 'Saturday', 16: 'Friday', 8: 'Thursday', 4: 'Wednesday', 2: 'Tuesday', 1: 'Monday'}
    schedule = []

    if repeat_schedule_value == 127:
        schedule.append('Every Day')
        return schedule
    elif repeat_schedule_value == 0:
        schedule.append('Never')
        return schedule

    for day in days_list:
        if repeat_schedule_value > 0 and repeat_schedule_value >= day:
            repeat_schedule_value -= day
            schedule.append(days_list[day])
    return reversed(schedule)

__artifacts__ = {
    "alarms": (
        "Alarms",
        ('*/mobile/Library/Preferences/com.apple.mobiletimerd.plist'),
        get_alarms)
}
