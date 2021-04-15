    
import os
import sys
import logging
import paramiko
import time
import re
import requests
import json
import datetime

sys.path.append('/home/work/tacase_dev/Resource')
from pet_ipalib import IpaMmlItem
log_level = logging.DEBUG


fb_info =   {
            'FB2101':'2021,1,6-2021,2,2',
            'FB2102':'2021,2,3-2021,3,2',
            'FB2103':'2021,3,3-2021,3,30',
            'FB2104':'2021,3,31-2021,4,27',
            'FB2105':'2021,4,28-2021,5,25',
            'FB2106':'2021,5,26-2021,6,22',
            'FB2107':'2021,6,23-2021,7,20',		
            'FB2108':'2021,7,21-2021,8,17',	
            'FB2109':'2021,8,18-2021,9,14',	
            'FB2110':'2021,9,15-2021,10,12',	
            'FB2111':'2021,10,13-2021,11,9',	
            'FB2112':'2021,11,10-2021,12,7',
            'FB2113':'2021,12,8-2022,1,4'
            }

class c_pet_rep_data(object):

    def __init__(self, aceesskey=''):
        logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)
        self.logger = logging.getLogger('rep_data')
        logging.basicConfig(
            format='%(asctime)s,%(msecs)d [REP_%(levelname)s] %(message)s',
            datefmt='%H:%M:%S',
            level=log_level)
        self.logger.setLevel(log_level)
        self.proxies = {}
        # self.set_proxy()

    def geturl(self, url):
        self.logger.debug('Retrieve url: {}'.format(url))
        data = {'username': "a3liu", 'password': "xxxxxx"}
        headers = {'content-type': 'application/json',
                   'referer':'https://rep-portal.wroclaw.nsn-rdnet.net/login/',
                   'origin': 'https://rep-portal.wroclaw.nsn-rdnet.net',
                   'cookie': 
                   '_pk_id.1.6f59=add46117cb0942a5.1587967678.; _pk_id.2.6f59=a39d50439c088dfa.1588741853.9.1614676650.1614676650.; _pk_ses.1.6f59=1',
                   'user-agent':
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}
        login_url = 'https://rep-portal.wroclaw.nsn-rdnet.net/jwt/obtain/'
        rn1 = requests.post(login_url, headers=headers, data=json.dumps(data))
        print(rn1)
        if rn1.status_code == 200:
            # token = json.loads(rn1.text)['token']
            csrftoken =   json.loads(rn1.text)['csrftoken']
            sessionid = json.loads(rn1.text)['sessionid']
            cookie =  '_pk_id.1.6f59=add46117cb0942a5.1587967678.; _pk_id.2.6f59=a39d50439c088dfa.1588741853.9.1614676650.1614676650.;\
                        _pk_ses.1.6f59=1; sessionid={}; csrftoken={}'.format(sessionid, csrftoken)
            headers = {'content-type': 'application/json',
            'referer':'https://rep-portal.wroclaw.nsn-rdnet.net/login/',
            'origin': 'https://rep-portal.wroclaw.nsn-rdnet.net',
            'cookie': cookie,
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}    
            rn = requests.get(url, headers=headers, proxies=self.proxies)
            # rn = requests.get(url, headers=headers)
            if rn.status_code == 200:
                return rn.content.decode(rn.apparent_encoding)
            else:
                raise Exception('Get URL {} failed'.format(url))
        else:
            raise Exception('Login URL {} failed'.format(login_url))

    def get_case_data(self, team, releases, domain, project, test_entity, limit):
        url = 'https://rep-portal.wroclaw.nsn-rdnet.net/api/qc/instances/report/?fields=no,id,status_color,\
tep_status_color,qc_id__id,test_set__qc_id,test_case__qc_id,url,fault_report_id_link,origin,m_path,\
test_set__name,name,test_case__path,test_plan_folder,status,platform,priority,test_subarea,test_object,\
test_entity,test_lvl_area,ca,organization,phase,det_auto_lvl,fault_report_id,res_tester,res_tester_email,feature,features,\
requirement,acceptance_criteria,delivery_package,suspension_end,pronto_view_type,last_testrun__timestamp,add_test_run&limit={}&\
organization__pos_neg=%22{}%22&origin__domain__pos_neg={}&\
origin__project__pos_neg={}&portal__releases={}&test_entity__pos_neg={}&ti_scope=true'.format(
    limit, team, domain, project, releases, test_entity)
        self.logger.info(url)
        try:
            resonse = self.geturl(url)
            return resonse
        except:
            import traceback
            self.logger.error(traceback.print_exc())
            raise Exception('Get URL {} failed'.format(url))

    def _get_data(self, test_entity):
        team = 'SRAN_Prod_HZH_RRM_6_Vrf'
        releases = 'SBTS00'
        domain = 'MN_SRAN'
        project = 'SRAN_SBTS'
        limit='500'
        return self.get_case_data(team, releases, domain, project, test_entity, limit)

    def _get_link(self, test_entity):
        team = 'SRAN_Prod_HZH_RRM_6_Vrf'
        releases = 'SBTS00'
        domain = 'MN_SRAN'
        project = 'SRAN_SBTS'
        link = "https://rep-portal.wroclaw.nsn-rdnet.net/reports/qc/?organization=%22{}%22&releases={}&\
domain={}&project={}&ti_scope=true&test_entity={}".format(team, releases, domain, project, test_entity)
        return link

    def get_cit_data(self):
        self.cit_data=self._get_data('cit')
        return self.cit_data
    
    def get_crt_data(self):
        self.crt_data=self._get_data('crt')
        return self.crt_data

    def get_manual_data(self):
        self.manual_data=self._get_data('manual')
        return self.manual_data
    
    def analysis_execute_data(self, data, test_entity):
        data = json.loads(data)
        count = data['count']
        results = data['results']
        test_results = []
        tester_list = []
        for i in results:
            test = IpaMmlItem()
            test.qc_id = i['qc_id']['id']
            test.res_tester = i['res_tester']
            test.res_tester_email = i['res_tester_email']
            test.fault_id = i['fault_report_id_link'][0]['id']
            test.fault_color = i['fault_report_id_link'][0]['color']
            test.fault_link = i['fault_report_id_link'][0]['link']
            if test.res_tester not in tester_list:
                tester_list.append(test.res_tester)
            test.status = i['status']
            # last_runtime = i['last_testrun']['timestamp'].split('T')[0]
            # test.last_runtime = datetime.datetime.strptime(last_runtime, "%Y-%m-%d").strftime("%Y-%m-%d")
            if i['last_testrun'] == None:
                last_runtime = 'NULL'
                test.last_runtime = 'NULL'
            else:
                last_runtime = i['last_testrun']['timestamp'].split('T')[0]
                test.last_runtime = datetime.datetime.strptime(last_runtime, "%Y-%m-%d").strftime("%Y-%m-%d")
            test_results.append(test)
        count_case_results = []
        count_pr_status = []
        norun_testers_email = []
        title = 'Tester,Total,Passed,Failed,Norun,Executable Days,Start Date,Deadline,FB'
        count_case_results.append(title)
        title_pr = 'Tester,Case Id,Pronto Id,Pronto Status,Link'
        count_pr_status.append(title_pr)
        for tester in tester_list:
            total_num = 0
            passed_num = 0
            failed_num = 0
            norun_num = 0
            all_total_num = 0
            all_passed_num = 0
            all_failed_num = 0
            all_norun_num = 0
            fb, executable_days, starttime, deadline =  self.get_deadline_for_case(test_entity)
            for j in test_results:
                all_total_num +=1
                if j['last_runtime'] == 'NULL':
                    all_norun_num += 1
                    if j.res_tester_email not in norun_testers_email:
                        norun_testers_email.append( j.res_tester_email)
                else:
                    if j.status == 'Failed':
                        all_failed_num += 1
                    else:
                        if j.last_runtime >= starttime and j.last_runtime <= deadline:
                            if j.status == 'Passed':
                                all_passed_num +=1
                        else:
                            all_norun_num += 1
                            if j.res_tester_email not in norun_testers_email:
                                norun_testers_email.append( j.res_tester_email)
                if j.res_tester == tester:
                    total_num += 1
                    if j['last_runtime'] == 'NULL':
                        norun_num += 1
                    else:
                        if j['status'] == 'Failed':
                            failed_num += 1
                        else:
                            if j.last_runtime >= starttime and j.last_runtime <= deadline:
                                if j.status == 'Passed':
                                    passed_num += 1
                            else:
                                norun_num += 1 
            line = '{},{},{},{},{},{},{},{},{}'.format(tester, total_num, passed_num, failed_num, norun_num, executable_days, starttime, deadline, fb)
            count_case_results.append(line)
        total_line = '{},{},{},{},{},{},{},{},{}'.format('Total Num', all_total_num, all_passed_num, all_failed_num, all_norun_num, executable_days, starttime, deadline, fb)
        count_case_results.append(total_line)

        for j in test_results:
            if j.fault_id:
                line_pr = '{},{},{},{},{}'.format(j.res_tester, j.qc_id, j.fault_id, j.fault_color, j.fault_link)
                count_pr_status.append(line_pr)
                if j.fault_color.lower() == 'green' and j.res_tester_email not in norun_testers_email:
                    norun_testers_email.append( j.res_tester_email)
        return count_case_results,count_pr_status,executable_days,norun_testers_email
        
    def get_fb_info(self):
        #'FB2101':'1,6,2021-2,2,2021',
        fb_list = []
        for k,v in fb_info.items():
            info = IpaMmlItem()
            info.fb = k
            info.startdate = datetime.datetime.strptime(v.split('-')[0].replace(',','-'), "%Y-%m-%d").strftime("%Y-%m-%d")            
            info.enddate = datetime.datetime.strptime(v.split('-')[1].replace(',','-'), "%Y-%m-%d").strftime("%Y-%m-%d")
            info.middate = (datetime.datetime.strptime(info.startdate, "%Y-%m-%d") + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
            fb_list.append(info)
        return fb_list

    def get_deadline_for_case(self, test_entity):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        fb_list = self.get_fb_info()
        for i in fb_list:
            if test_entity.lower() == "manual":
                if today >= i.startdate and today <= i.enddate:
                    fb = i.fb
                    starttime = i.startdate
                    deadline = i.enddate 
            elif test_entity.lower() == "crt":
                if today >= i.startdate and today <= i.middate:
                    fb = i.fb
                    starttime = i.startdate
                    deadline = i.middate 
                if today > i.middate and today <= i.enddate:
                    fb = i.fb
                    starttime = i.middate
                    deadline = i.enddate 
            elif test_entity.lower() == "cit":
                if today >= i.startdate and today <= i.enddate:
                    fb = i.fb
                yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
                starttime = yesterday
                deadline = today
        executable_days = (datetime.datetime.strptime(deadline,'%Y-%m-%d')- datetime.datetime.strptime(today,'%Y-%m-%d')).days   
        return fb,executable_days,starttime,deadline

    def mail_print_in_table(self, lines, release, test_entity):
        output = ['<h4><font color="#003399">{} Report({})</font></h4>'.format(test_entity.upper(), release.upper())]
        output.append('<table border=1 style="border-collapse: collapse;" bordercolor="#ccc" cellpadding=4 cellspacing=0 width ="80%">')
        for i in range(len(lines)):
            output.append('<tr>')      
            tstr = 'th' if i == 0 else 'td'
            # tstr = 'td'
            # colorbg_line = ''
            # if lines[i].split('|')[1] == lines[i].split('|')[2]:
            #     colorbg_line = 'bgcolor="#8FBC8B"'
            # for item in lines[i].split('|'):
            #     if  not item.isdigit() and item.lower() in ['tester', 'total', 'passed', 'failed', 'norun', 'executable days', 'start date',
            #     'deadline', 'fb', 'case id', 'pronto id', 'pronto status', 'link', 'need run']:
            #         colorword = 'color="#666"' 
            #         colorbg = 'bgcolor="#d4d4d4"'
            #     elif item.lower() == 'green':
            #         colorword = 'color="green"'
            #     elif item.lower() == 'red':
            #         colorword = 'color="red"'
            #     elif item == lines[i].split('|')[0]:
            #         colorword = 'color="#666"'
            #         colorbg = 'style="font-weight:bold"'
            #     elif item.isdigit():
            #         colorword = 'color="#666"'
            #         colorbg = colorbg_line
            #     else:
            #         colorword = 'color="#666"'
            #         colorbg = ''
            colorbg_line = ''
            norun_flag = ''
            if 'case' in test_entity:
                if lines[i].split('|')[1] == lines[i].split('|')[2] and int(lines[i].split('|')[1]) != 0:
                    norun_flag = 'green'
                executable_days  = lines[i].split('|')[5]
                norun_num = lines[i].split('|')[4]
                yellow_days = 5
                red_days = 2
                if executable_days.isdigit() and int(executable_days) <= yellow_days and int(executable_days) >red_days and norun_num.isdigit() and int(norun_num) > 0:
                    norun_flag = 'yellow'
                if executable_days.isdigit() and int(executable_days) <=red_days and int(executable_days) >0 and norun_num.isdigit() and int(norun_num) > 0:
                    norun_flag = 'red'
            for j in range(len(lines[i].split('|'))):
                item = lines[i].split('|')[j]
                if 'https://' in item:
                    line = '<td><a href="{}">Case Link</a></td>'.format(item)
                    output.append(line)
                    output.append('</tr>')
                    continue
                if  not item.isdigit() and item.lower() in ['tester', 'total', 'passed', 'failed', 'norun', 'executable days', 'start date',
                'deadline', 'fb', 'case id', 'pronto id', 'pronto status', 'link', 'need run']:
                    colorword = 'color="#666"' 
                    colorbg = 'bgcolor="#d4d4d4"'
                elif item.lower() == 'green':
                    colorword = 'color="green"'
                elif item.lower() == 'red':
                    colorword = 'color="red"'
                elif item.lower() == 'orange':
                    colorword = 'color="orange"'
                elif item.lower() == "yellow":
                    colorword = 'color="#FFCC00"'
                elif item == lines[i].split('|')[0]:
                    colorword = 'color="#666"'
                    colorbg = 'style="font-weight:bold"'
                elif item.isdigit():
                    colorword = 'color="#666"'
                    colorbg = colorbg_line
                else:
                    colorword = 'color="#666"'
                    colorbg = ''
                if norun_flag == 'yellow':
                    if j == 4:
                        colorbg = 'bgcolor="#f3d751"'
                if norun_flag == 'red':
                    if j == 4:
                        colorbg = 'bgcolor="#f1707d"'
                if norun_flag == 'green':
                    if j in [1,2,3,4]:
                        colorbg = 'bgcolor="#8FBC8B"'
                output.append('<{} style="text-align:center" {}><font {}>{}</{}>'.format(tstr, colorbg, colorword, item, tstr))
            output.append('</tr>')
        output.append('</table>')
        if 'case' in test_entity.lower():
            output.append('Click the link: {}'.format(self._get_link(test_entity.lower().split()[0])))
        output.append('<br/>')
        return output

    def trasfer_data_to_table(self, content, release, test_entity):
        table = []
        if len(content) != 0:
            for x in range(len(content)):
                strline = content[x].replace(',','|')
                table.append(strline)
        table_message = self.mail_print_in_table(table, release, test_entity)
        return table_message
    

    def gen_email(self, table_message):
        import smtplib
        from email.mime.text import MIMEText
        from email.header import Header
        from email.utils import formatdate
        date = time.strftime("%Y-%m-%d")        
        if int(self.crt_executable_days) <=5 or int(self.manual_executable_days) <=5:
            level =  '[Remind]'
        else:
            level =  ''

        mail_host="smtp.XXX.com"
        # sender = 'amy.c.liu@nokia-sbell.com'
        sender = 'I_MN_HZ_RRM6_TA@nokia-sbell.com'
        if level or datetime.datetime.now().weekday() + 1 == 3:
            all_norun_addr = self.get_all_norun_addr() + ['liguo.zhang@nokia-sbell.com']
        else:
            all_norun_addr = []
        # all_norun_addr = []
        self.logger.info(all_norun_addr)
        receivers = ['amy.c.liu@nokia-sbell.com']
        receivers = receivers + all_norun_addr
        self.logger.info(receivers)
        smtp_server = 'mail.emea.nsn-intra.net' 

        mail_msg = "<p>REP Case Execution Result, Send By TA...</p>"
        mail_message = []
        mail_message.append(mail_msg)
        mail_message.append("<html><head></head><body>")
        for line in table_message:
            mail_message.append(line)
        mail_message.append("</body></html>")
        try:
            smtp = smtplib.SMTP(smtp_server) 
            msg = MIMEText('\n'.join(mail_message), 'html', 'utf-8')            
            from_ = sender
            to_   = ";".join(str(i) for i in receivers)
            
            msg['From'] = from_
            msg['To'] = to_
            subject = '{} ALL Rep-portal Report {}'.format(level, date)
            msg['Subject'] =  Header(subject, 'utf-8')
            smtp.sendmail(sender, receivers, msg.as_string())
            self.logger.info('Send mail to %s successful, please check it.\n' %(to_))
        except smtplib.SMTPException as e:
            self.logger.info("Error: Send mail failed!")
            self.logger.info(e)

    def get_and_analysis_cit_data(self):
        self.get_cit_data()
        self.cit_result, self.cit_pr_results, self.cit_executable_days, self.cit_norun_testers_email = c.analysis_execute_data(c.cit_data, 'cit')

    def get_and_analysis_crt_data(self):
        self.get_crt_data()
        self.crt_result, self.crt_pr_results, self.crt_executable_days, self.crt_norun_testers_email = c.analysis_execute_data(c.crt_data, 'crt')

    def get_and_analysis_manual_data(self):
        self.get_manual_data()
        self.manual_result, self.manual_pr_results, self.manual_executable_days, self.manual_norun_testers_email = c.analysis_execute_data(c.manual_data, 'manual')

    def get_all_norun_addr(self):
        if int(self.crt_executable_days) <=5 and  int(self.manual_executable_days) >5:
            all_norun_addr = c.cit_norun_testers_email + c.crt_norun_testers_email
        elif int(self.manual_executable_days) <=5 and int(self.crt_executable_days) >5:
            all_norun_addr = c.cit_norun_testers_email + c.manual_norun_testers_email
        elif int(self.manual_executable_days) <=5 and int(self.crt_executable_days) <=5:
            all_norun_addr = c.cit_norun_testers_email + c.crt_norun_testers_email + c.manual_norun_testers_email
        else:
            all_norun_addr = []
        return all_norun_addr

if __name__ == '__main__':
    c= c_pet_rep_data()
    c.get_and_analysis_cit_data()
    time.sleep(3)
    c.get_and_analysis_crt_data()
    time.sleep(3)
    c.get_and_analysis_manual_data()
    message1 = c.trasfer_data_to_table(c.cit_result, 'trunk', 'cit case')
    message2 = c.trasfer_data_to_table(c.crt_result, 'trunk', 'crt case')
    message3 = c.trasfer_data_to_table(c.manual_result, 'trunk', 'manual case')
    message4 = c.trasfer_data_to_table(c.cit_pr_results, 'trunk', 'cit pronto')
    message5 = c.trasfer_data_to_table(c.crt_pr_results, 'trunk', 'crt pronto')
    message6 = c.trasfer_data_to_table(c.manual_pr_results, 'trunk', 'manual pronto')
    messages = message1 + message2 + message3 + message4 + message5 + message6
    c.gen_email(messages)
    pass


    
