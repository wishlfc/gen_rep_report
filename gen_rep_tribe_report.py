    
import os
import sys
import logging
import time
import re
import requests
import json
import datetime

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
team_lpo = {
            'SRAN_Prod_HZH_RRM_1_Vrf': 'jian.jia@nokia-sbell.com',
            'SRAN_Prod_HZH_RRM_2_Vrf': 'liefeng.he@nokia-sbell.com',
            'SRAN_Prod_HZH_RRM_3_Vrf': 'jiana.song@nokia-sbell.com',
            'SRAN_Prod_HZH_RRM_4_Vrf': 'feiyan.chen@nokia-sbell.com',
            'SRAN_Prod_HZH_RRM_5_Vrf': 'haihua.wu@nokia-sbell.com',
            'SRAN_Prod_HZH_RRM_6_Vrf': 'liguo.zhang@nokia-sbell.com'
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
        time.sleep(1)
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
            # PROXY = '10.144.1.10:8080'
            # PROXIES = dict(https=PROXY, http=PROXY)
            rn = requests.get(url, headers=headers, proxies={})
            if rn.status_code == 200:
                return rn.content.decode(rn.apparent_encoding)
            else:
                raise Exception('Get URL {} failed'.format(url))
        else:
            raise Exception('Login URL {} failed'.format(login_url))

    def get_tribe_case_data(self, ca, releases, domain, project, test_entity, limit):
        url = 'https://rep-portal.wroclaw.nsn-rdnet.net/api/qc/instances/report/?ca__pos_neg={}&fields=no,id,status_color,\
wall_status,tep_status_color,qc_id__id,test_set__qc_id,test_case__qc_id,url,fault_report_id_link,origin,m_path,\
test_set__name,name,test_case__path,test_plan_folder,status,platform,priority,test_subarea,test_object,\
test_entity,test_lvl_area,ca,organization,phase,det_auto_lvl,fault_report_id,res_tester,res_tester_email,feature,features,\
requirement,acceptance_criteria,delivery_package,suspension_end,pronto_view_type,last_testrun__timestamp,add_test_run&limit={}&origin__domain__pos_neg={}&\
origin__project__pos_neg={}&portal__releases={}&test_entity__pos_neg={}&ti_scope=true'.format(ca,
    limit, domain, project, releases, test_entity)
        self.logger.info(url)
        try:
            resonse = self.geturl(url)
            return resonse
        except:
            import traceback
            self.logger.error(traceback.print_exc())
            raise Exception('Get URL {} failed'.format(url))

    def _get_tribe_data(self, test_entity):
        releases = 'SBTS00'
        domain = 'MN_SRAN'
        project = 'SRAN_SBTS'
        limit='1000'
        ca = 'SRAN_Prod_RRM'
        tribe_info = self.get_tribe_case_data(ca, releases, domain, project, test_entity, limit)
        tribe_info = json.loads(tribe_info)
        results = tribe_info['results']
        team_info = {}
        for team, lpo in team_lpo.items(): 
            team_result = []
            for i in results:
                if i['organization'] == team:
                    team_result.append(i)
            team_info[team] = team_result
        return team_info

    def _get_link(self, test_entity):
        team = 'SRAN_Prod_HZH_RRM_6_Vrf'
        releases = 'SBTS00'
        domain = 'MN_SRAN'
        project = 'SRAN_SBTS'
        link = "https://rep-portal.wroclaw.nsn-rdnet.net/reports/qc/?organization=%22{}%22&releases={}&\
domain={}&project={}&ti_scope=true&test_entity={}".format(team, releases, domain, project, test_entity)
        return link

    def _get_team_link(self, team, test_entity):
        # team = 'SRAN_Prod_HZH_RRM_6_Vrf'
        releases = 'SBTS00'
        domain = 'MN_SRAN'
        project = 'SRAN_SBTS'
        link = "https://rep-portal.wroclaw.nsn-rdnet.net/reports/qc/?organization=%22{}%22&releases={}&\
domain={}&project={}&ti_scope=true&test_entity={}".format(team, releases, domain, project, test_entity)
        return link
    
    def get_tribe_cit_data(self):
        self.cit_data=self._get_tribe_data('cit')
        return self.cit_data

    def get_tribe_crt_data(self):
        self.crt_data=self._get_tribe_data('crt')
        return self.crt_data

    def get_tribe_manual_data(self):
        self.manual_data=self._get_tribe_data('manual')
        return self.manual_data
    
    def analysis_tribe_execute_data(self, data, test_entity):
        count_case_results = []
        fb, executable_days, starttime, deadline =  self.get_deadline_for_case(test_entity)
        title = 'Team,Total,Passed,Failed,Norun,Executable Days,Start Date,Deadline,FB,Link'
        count_case_results.append(title)
        norun_team_lpo = []
        if test_entity.upper() == 'CIT':
            for team,team_info in data.items():
                team_total_num = int(len(team_info))
                link = self._get_team_link(team, test_entity)
                team_passed_num = 0
                team_failed_num = 0
                team_norun_num = 0
                for i in team_info:
                    if i['wall_status']['status'] == 'No Run':
                        team_norun_num += 1
                    if i['wall_status']['status'] == 'Failed':
                        team_failed_num += 1
                    if i['wall_status']['status'] == 'Passed':
                        team_passed_num +=1
                line = '{},{},{},{},{},{},{},{},{},{}'.format(
                    team, team_total_num, team_passed_num, team_failed_num, team_norun_num, executable_days, starttime, deadline, fb, link)
                count_case_results.append(line)
                if team_norun_num != 0:
                    norun_team_lpo.append(team_lpo[team])
        else:
            for team,team_info in data.items():
                team_total_num = int(len(team_info))
                link = self._get_team_link(team, test_entity)
                team_passed_num = 0
                team_failed_num = 0
                team_norun_num = 0
                for i in team_info:
                    if i['last_testrun'] == None:
                        last_runtime = 'NULL'
                        i['last_runtime'] = 'NULL'
                    else:
                        last_runtime = i['last_testrun']['timestamp'].split('T')[0]
                        i['last_runtime'] = datetime.datetime.strptime(last_runtime, "%Y-%m-%d").strftime("%Y-%m-%d")
                    if i['status'] == 'Failed':
                        team_failed_num += 1
                    else:
                        if i['last_runtime'] != 'NULL' and (i['last_runtime'] >= starttime and i['last_runtime'] <= deadline):
                            if i['status'] == 'Passed':
                                team_passed_num +=1
                        else:
                            team_norun_num += 1
                line = '{},{},{},{},{},{},{},{},{},{}'.format(
                    team, team_total_num, team_passed_num, team_failed_num, team_norun_num, executable_days, starttime, deadline, fb, link)
                count_case_results.append(line)
                if team_norun_num != 0:
                    norun_team_lpo.append(team_lpo[team])
        print(count_case_results)
        # print(norun_team_lpo)
        count_pr_status = []
        return count_case_results,count_pr_status,executable_days,norun_team_lpo

        
    def get_fb_info(self):
        #'FB2101':'1,6,2021-2,2,2021',
        fb_list = []
        for k,v in fb_info.items():
            info = {}
            info['fb'] = k
            info['startdate'] = datetime.datetime.strptime(v.split('-')[0].replace(',','-'), "%Y-%m-%d").strftime("%Y-%m-%d")            
            info['enddate'] = datetime.datetime.strptime(v.split('-')[1].replace(',','-'), "%Y-%m-%d").strftime("%Y-%m-%d")
            info['middate'] = (datetime.datetime.strptime(info['startdate'], "%Y-%m-%d") + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
            fb_list.append(info)
        return fb_list

    def get_deadline_for_case(self, test_entity):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        fb_list = self.get_fb_info()
        for i in fb_list:
            if test_entity.lower() == "manual":
                if today >= i['startdate'] and today <= i['enddate']:
                    fb = i['fb']
                    starttime = i['startdate']
                    deadline = i['enddate'] 
            elif test_entity.lower() == "crt":
                if today >= i['startdate'] and today <= i['middate']:
                    fb = i['fb']
                    starttime = i['startdate']
                    deadline = i['middate'] 
                if today > i['middate'] and today <= i['enddate']:
                    fb = i['fb']
                    starttime = i['middate']
                    deadline = i['enddate'] 
            elif test_entity.lower() == "cit":
                if today >= i['startdate'] and today <= i['enddate']:
                    fb = i['fb']
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
            colorbg_line = ''
            norun_flag = ''
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
            if executable_days.isdigit() and  int(executable_days) == 0 and norun_num.isdigit() and int(norun_num) > 0:
                norun_flag = 'gray'
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
                if norun_flag == 'gray':
                    if j ==4:
                        colorbg = 'bgcolor="#E0E0E0"'
                if norun_flag == 'green':
                    if j in [1,2,3,4]:
                        colorbg = 'bgcolor="#8FBC8B"'

                
                output.append('<{} style="text-align:center" {}><font {}>{}</{}>'.format(tstr, colorbg, colorword, item, tstr))
            output.append('</tr>')
        output.append('</table>')
        # if 'case' in test_entity.lower():
        #     output.append('Click the link: {}'.format(self._get_link(test_entity.lower().split()[0])))
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
    

    def gen_tribe_email(self, table_message):
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
        receivers = ['amy.c.liu@nokia-sbell.com']
        if level:
            norun_lpo_list = self.get_all_norun_addr() + ['xiaodan.gu@nokia-sbell.com']
            ccer = 'bo-chris.wang@nokia-sbell.com'
            self.logger.info('Stil has no run cases team:{}'.format(norun_lpo_list))
        else:
            norun_lpo_list = []
            ccer = ''
        # norun_lpo_list = []
        # ccer = ''
        receivers = receivers + norun_lpo_list
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
            cc_   = ccer
            
            msg['From'] = from_
            msg['Cc'] = cc_
            msg['To'] = to_
            # level = ''
            subject = '{} ALL SRAN Prod RRM Rep-portal Report {}'.format(level, date)
            msg['Subject'] =  Header(subject, 'utf-8')
            smtp.sendmail(sender, receivers, msg.as_string())
            self.logger.info('Send mail to %s successful, please check it.\n' %(to_))
        except smtplib.SMTPException as e:
            self.logger.info("Error: Send mail failed!")
            self.logger.info(e)

    def get_and_analysis_tribe_cit_data(self):
        self.get_tribe_cit_data()
        self.cit_result, self.cit_pr_results, self.cit_executable_days, self.cit_norun_team_lpo = c.analysis_tribe_execute_data(c.cit_data, 'cit')

    def get_and_analysis_tribe_crt_data(self):
        self.get_tribe_crt_data()
        self.crt_result, self.crt_pr_results, self.crt_executable_days, self.crt_norun_team_lpo = c.analysis_tribe_execute_data(c.crt_data, 'crt')

    def get_and_analysis_tribe_manual_data(self):
        self.get_tribe_manual_data()
        self.manual_result, self.manual_pr_results, self.manual_executable_days, self.manual_norun_team_lpo = c.analysis_tribe_execute_data(c.manual_data, 'manual')

    def get_all_norun_addr(self):
        if int(self.crt_executable_days) <=5 and  int(self.manual_executable_days) >5:
            all_norun_addr = c.cit_norun_team_lpo + c.crt_norun_team_lpo
        elif int(self.manual_executable_days) <=5 and int(self.crt_executable_days) >5:
            all_norun_addr = c.cit_norun_team_lpo + c.manual_norun_team_lpo
        elif int(self.manual_executable_days) <=5 and int(self.crt_executable_days) <=5:
            all_norun_addr = c.cit_norun_team_lpo + c.crt_norun_team_lpo + c.manual_norun_team_lpo
        else:
            all_norun_addr = []
        all_norun_addr = list(set(all_norun_addr))
        return all_norun_addr

if __name__ == '__main__':
    c= c_pet_rep_data()
    c.get_and_analysis_tribe_cit_data()
    time.sleep(3)
    c.get_and_analysis_tribe_crt_data()
    time.sleep(3)
    c.get_and_analysis_tribe_manual_data()
    message1 = c.trasfer_data_to_table(c.cit_result, 'trunk', 'cit case')
    message2 = c.trasfer_data_to_table(c.crt_result, 'trunk', 'crt case')    
    message3 = c.trasfer_data_to_table(c.manual_result, 'trunk', 'manual case')
    messages = message1 + message2 + message3
    c.gen_tribe_email(messages)
    pass


