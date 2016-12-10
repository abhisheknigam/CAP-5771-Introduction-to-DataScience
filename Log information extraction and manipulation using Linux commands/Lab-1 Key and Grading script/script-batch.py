import commands
import glob
import numpy as np
import re

# Return [0-9] for the grade of submission
# Return None if number of lines not equal to len(expected_outputs)
# 
def Grade(path_to_file, expected_outputs):
	with open(path_to_file,'r') as f:
		lines = f.read().strip().split('\n')
		if len(lines) != len(expected_outputs):
			return None
		# run each line of command
		grades = []
		for k in xrange(len(lines)):
			c = lines[k].strip()
			# fix issue #1: incorrect path of wc_day6_1.log
			m = re.compile('(.)* ([^ ]*)wc_day6_1.log(.)*').match(c)
			if m is not None:
				path = m.group(2)
				if path != '~/':
					c = c.replace(path+'wc_day6_1.log', '~/wc_day6_1.log')
			# execute the command and get output
			try:
				output = commands.getstatusoutput(c)[1]
			except:
				grades.append(0)
				continue
			if k == 8:
				# For the Q9, we need special treatment due to variations.
				grades.append(q9_judge(output))
			elif k == 3:
				# For the Q4, it is ok to have path along with file names.
				grades.append(q4_judge(output))
			else:
				if output == expected_outputs[k]:
					grades.append(1)
				elif k == 4 or k == 5 or k == 7:
					# A bug in pipe: need to skip error message of grep.
					if '\n'.join(output.split('\n')[:-1]) == expected_outputs[k]:
						grades.append(1)
					else:
						grades.append(0)
				else:
					grades.append(0)
	assert len(grades) == len(expected_outputs)
	return grades

def q4_judge(output):
	lines = output.split('\n')
	# must have 3 lines
	if len(lines) != 3:
		return 0
	# 1st line must contain '4.JPG'
	if lines[0].find('4.JPG') == -1:
		return 0
	# 2nd line must contain '3.JPG'
	if lines[1].find('3.JPG') == -1:
		return 0
	# 3rd line must contain '2.JPG'
	if lines[2].find('2.JPG') == -1:
		return 0
	return 1
def q9_judge(output):
	# it must has 3 lines
	if output.count('\n') != 2:
		return 0
	# it must have 3 occurrences of 'HTTP'
	if output.count('HTTP') != 3:
		return 0
	# it must contain these numbers: 953944, 239271 and 138
	if output.find('953944') == -1 or output.find('239271') == -1 or output.find('138') == -1:
		return 0
	return 1

# Declare expected outputs
expected_outputs = [
	"/cise/homes/dihong/TA-FA16/hw1/testdir",
	"1",
	"3",
	"4.JPG\n3.JPG\n2.JPG",
	"5 - - [30/Apr/1998:22:00:04 +0000] \"GET /images/hm_f98_top.gif HTTP/1.1\" 200 915\n6 - - [30/Apr/1998:22:00:04 +0000] \"GET /images/team_hm_concacaf.gif HTTP/1.0\" 200 764\n6 - - [30/Apr/1998:22:00:04 +0000] \"GET /images/team_hm_afc.gif HTTP/1.0\" 200 475\n6 - - [30/Apr/1998:22:00:04 +0000] \"GET /images/team_hm_caf.gif HTTP/1.0\" 200 473\n7 - - [30/Apr/1998:22:00:05 +0000] \"GET /english/playing/mascot/mascot.html HTTP/1.0\" 200 5521\n1 - - [30/Apr/1998:22:00:05 +0000] \"GET /images/home_tool.gif HTTP/1.0\" 200 327\n8 - - [30/Apr/1998:22:00:05 +0000] \"GET /english/images/comp_bu_stage1n.gif HTTP/1.0\" 200 1548\n8 - - [30/Apr/1998:22:00:05 +0000] \"GET /english/images/comp_bu_stage2n_on.gif HTTP/1.0\" 200 996\n8 - - [30/Apr/1998:22:00:05 +0000] \"GET /images/comp_stage2_brc_top.gif HTTP/1.0\" 200 163\n8 - - [30/Apr/1998:22:00:05 +0000] \"GET /images/comp_stage2_brc_topr.gif HTTP/1.0\" 200 163\n9 - - [30/Apr/1998:22:00:05 +0000] \"GET /english/history/past_cups/images/posters/france38.gif HTTP/1.0\" 200 4649",
	"2196 - - [01/May/1998:00:00:00 +0000] \"GET /images/nav_bg_top.gif HTTP/1.0\" 200 929\n2096 - - [01/May/1998:00:00:00 +0000] \"GET /images/news_hm_arw.gif HTTP/1.1\" 200 152\n2065 - - [01/May/1998:00:00:00 +0000] \"GET /images/s102373.gif HTTP/1.0\" 200 142\n2219 - - [01/May/1998:00:00:00 +0000] \"GET /english/frntpage.htm HTTP/1.0\" 200 12800\n2168 - - [01/May/1998:00:00:00 +0000] \"GET /french/images/team_group_header_e.gif HTTP/1.1\" 200 724\n2168 - - [01/May/1998:00:00:00 +0000] \"GET /images/s102378.gif HTTP/1.1\" 200 118\n2168 - - [01/May/1998:00:00:00 +0000] \"GET /images/s102324.gif HTTP/1.1\" 200 176\n2206 - - [01/May/1998:00:00:01 +0000] \"GET /images/s102325.gif HTTP/1.0\" 200 187\n2096 - - [01/May/1998:00:00:01 +0000] \"GET /images/32t49814.jpg HTTP/1.1\" 200 5196\n1995 - - [01/May/1998:00:00:01 +0000] \"GET /english/venues/images/venue_hm_bg01.jpg HTTP/1.0\" 200 44591",
	"402\n1541\n1771\n2548\n4070\n5593\n7068\n9573\n9833\n10000\n10228\n10482\n10560\n10581",
	"\"GET /images/home_intro.anim.gif HTTP/1.0\" 200 60349\n\"GET /images/home_bg_stars.gif HTTP/1.0\" 200 2557\n\"GET /images/home_fr_phrase.gif HTTP/1.0\" 200 2843\n\"GET /images/nav_bg_top.gif HTTP/1.0\" 200 929\n\"GET /images/home_logo.gif HTTP/1.0\" 200 3401\n\"GET /images/logo_cfo.gif HTTP/1.0\" 200 1504\n\"GET /images/home_eng_phrase.gif HTTP/1.0\" 200 2861\n\"GET /english/index.html HTTP/1.0\" 304 0\n\"GET /english/frntpage.htm HTTP/1.0\" 200 12800\n\"GET /images/hm_f98_top.gif HTTP/1.1\" 200 915",
	"953944 HTTP/1.0\n239271 HTTP/1.1\n138 HTTP/X.X"
	]
    
# Verify the groundtruth answers
actual_grade = sum(Grade('../hw1.ans', expected_outputs))
if actual_grade != len(expected_outputs):
	print Grade('../hw1.ans', expected_outputs)
assert actual_grade == len(expected_outputs), "Actual grade = %d, expected = %d" % (actual_grade, len(expected_outputs))
# Load submissions
sub = glob.glob("../submissions/*.txt")
assert len(sub) > 0
print "Load %d submissions." % len(sub)
# Grading
#grades = [(s.split('_')[2], Grade(s, expected_outputs)) for s in sub]  # [(stu_id, grade)]
total_per_questions = np.zeros(len(expected_outputs))
nb_to_run = len(sub)
nb_valid_runs = 0
for k in range(nb_to_run):
	score = Grade(sub[k], expected_outputs)
	if score is not None:
		total_per_questions = total_per_questions + np.array(score)
		nb_valid_runs = nb_valid_runs + 1
		print score, sub[k], sum(score)
	else:
		print "None - ", sub[k]
print "Average score", [round(f*100)/100.0 for f in total_per_questions/float(nb_valid_runs)]


