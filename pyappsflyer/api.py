from typing import Optional, List

from .base import BaseAppsFlyer
from .settings import DEFAULT_TIMEZONE


class PerformanceReport(BaseAppsFlyer):

    report_names = (
        'partners_report', 'partners_by_date_report',
        'daily_report', 'geo_report', 'geo_by_date_report'
    )

    def _get_report(self,
                    from_date: Optional = None,
                    to_date: Optional = None,
                    timezone: str = DEFAULT_TIMEZONE,
                    api_report_name: str = "partners_report",
                    copy_to_csv: bool = False,
                    copy_to_json: bool = False):
        """
        Method to receive one performance report.
        If dates are not presented default number of days will be used.

        :param from_date: from what date to begin, date format - YYYY-MM-DD
        :param to_date: at what date to end, date format - YYYY-MM-DD
        :param timezone: timezone for api request, default - Europe/Moscow
        :param api_report_name: name of the performance report according to api documentation
        :param copy_to_csv: save a .csv file copy
        :param copy_to_json: save a .json file copy
        :return: Ordered dictionary created from CSV file
        """
        self.validate_dates_and_report_names(api_report_name, self.report_names, from_date, to_date)
        self.api_report_name = api_report_name

        if not from_date or not to_date:
            from_date, to_date = self.get_default_dates()

        return self._get_csv(request_args={"from": from_date,
                                           "to": to_date,
                                           "timezone": timezone})

    def get_reports(self,
                    exclude_reports: Optional[List[str]] = None,
                    *args,
                    **kwargs) -> list:
        """
        Method to receive all reports

        :param exclude_reports: an array with names of reports needs to be excluded in string format
        :return: list with results
        """
        all_reports = []

        if exclude_reports:
            self.report_names = self.do_reports_exclusion(self.report_names,
                                                          exclude_reports)

        for report_name in self.report_names:
            all_reports.append({report_name: self.get_report(api_report_name=report_name, *args, **kwargs)})

        return all_reports


class RawDataReport(BaseAppsFlyer):

    additional_fields_uninstall_query = (
        "gp_referrer", "gp_click_time",
        "gp_install_begin", "amazon_aid", "keyword_match_type"
    )

    additional_fields = (
        "install_app_store", "contributor1_match_type",
        "contributor2_match_type", "contributor3_match_type",
        "match_type", "device_category",
    ) + additional_fields_uninstall_query

    special_report_names = (
        'uninstall_events_report',
    )

    report_names = (
        'installs_report',
        'in_app_events_report',
        'organic_installs_report',
        'organic_in_app_events_report',
    ) + special_report_names

    report_with_retargeting = (
        'installs_report',
        'in_app_events_report'
    )

    def _get_report(self,
                    from_date: Optional = None,
                    to_date: Optional = None,
                    timezone: str = DEFAULT_TIMEZONE,
                    api_report_name: str = "installs_report",
                    retargeting: bool = False,
                    different_additional_fields: bool = False,
                    copy_to_csv: bool = False,
                    copy_to_json: bool = False):
        """
        Method to receive one performance report.
        If dates are not presented default number of days will be used.

        :param from_date: from what date to begin, date format - YYYY-MM-DD
        :param to_date: at what date to end, date format - YYYY-MM-DD
        :param timezone: timezone for api request, default - Europe/Moscow
        :param api_report_name: name of the performance report according to api documentation
        :param retargeting: use retargeting params for reports or not
                            default: False
        :param different_additional_fields: fields to add into report, more info in AppsFlyer docs
        :param copy_to_csv: save a .csv file copy
        :param copy_to_json: save a .json file copy
        :return: Ordered dictionary created from CSV file
        """
        self.validate_dates_and_report_names(api_report_name, self.report_names, from_date, to_date)
        self.api_report_name = api_report_name

        if not from_date or not to_date:
            from_date, to_date = self.get_default_dates()

        request_args = {"from": from_date,
                        "to": to_date,
                        "timezone": timezone,
                        "additional_fields": ",".join(self.additional_fields)}

        if different_additional_fields:
            request_args["additional_fields"] = ",".join(self.additional_fields_uninstall_query)

        if retargeting:
            request_args.update({"reattr": "true"})

        return self._get_csv(request_args=request_args)

    def get_reports(self,
                    exclude_reports: Optional[List[str]] = None,
                    exclude_retargeting_reports: Optional[tuple] = None,
                    *args,
                    **kwargs):
        """
        Method to receive all reports

        :param exclude_reports: an array with names of reports needs to be excluded in string format
        :param exclude_retargeting_reports:  an array with names of retargeting
                                             reports needs to be excluded in string format
        :return: list with results
        """

        all_reports = []

        if exclude_reports:
            self.report_names = self.do_reports_exclusion(self.report_names,
                                                          exclude_reports)

        if exclude_retargeting_reports:
            self.report_names = self.do_reports_exclusion(self.report_with_retargeting,
                                                          exclude_retargeting_reports)

        for report_name in self.report_names:
            if report_name in self.report_with_retargeting:
                all_reports.append({report_name: self.get_report(api_report_name=report_name, *args, **kwargs)})
                all_reports.append({f"{report_name}_retargeting": self._get_report(api_report_name=report_name,
                                                                                   retargeting=True,
                                                                                   *args, **kwargs)})
            elif report_name in self.special_report_names:
                all_reports.append({report_name: self.get_report(api_report_name=report_name,
                                                                  different_additional_fields=True,
                                                                  *args, **kwargs)})
            else:
                all_reports.append({report_name: self.get_report(api_report_name=report_name, *args, **kwargs)})
        return all_reports


class TargetingValidationRulesReport(BaseAppsFlyer):

    additional_fields = ("rejected_reason", "rejected_reason_value",
                         "contributor1_match_type", "contributor2_match_type",
                         "contributor3_match_type", "match_type,device_category",
                         "gp_referrer", "gp_click_time", "gp_install_begin",
                         "amazon_aid", "keyword_match_type"
    )

    report_names = (
        'invalid_installs_report',
        'invalid_in_app_events_report'
    )

    def _get_report(self,
                    from_date: Optional = None,
                    to_date: Optional = None,
                    timezone: str = DEFAULT_TIMEZONE,
                    api_report_name: str = "invalid_installs_report",
                    copy_to_csv: bool = False,
                    copy_to_json: bool = False):
        """
        Method to receive one performance report.
        If dates are not presented default number of days will be used.

        :param from_date: from what date to begin, date format - YYYY-MM-DD
        :param to_date: at what date to end, date format - YYYY-MM-DD
        :param timezone: timezone for api request, default - Europe/Moscow
        :param api_report_name: name of the performance report according to api documentation
        :param copy_to_csv: save a .csv file copy
        :param copy_to_json: save a .json file copy
        :return: Ordered dictionary created from CSV file
        """
        self.validate_dates_and_report_names(api_report_name, self.report_names, from_date, to_date)
        self.api_report_name = api_report_name

        if not from_date or not to_date:
            from_date, to_date = self.get_default_dates()

        request_args = {"from": from_date,
                        "to": to_date,
                        "timezone": timezone,
                        "additional_fields": ",".join(self.additional_fields)}

        return self._get_csv(request_args=request_args)

    def get_reports(self,
                    exclude_reports: Optional[list] = None,
                    *args,
                    **kwargs):
        """
        Method to receive all reports

        :param exclude_reports: an array with names of reports needs to be excluded in string format
        :return: list with results
        """
        all_reports = []

        if exclude_reports:
            self.report_names = self.do_reports_exclusion(self.report_names, exclude_reports)

        for report_name in self.report_names:
            all_reports.append({report_name: self.get_report(api_report_name=report_name, *args, **kwargs)})

        return all_reports
