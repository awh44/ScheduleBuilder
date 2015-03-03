#!/usr/bin/python

import sys
import urllib
import re

URLS = [
"https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAADWLTQ6CMBBGR4w%2Fa%2BNeLmChoiuXGldsjFxgpBNS0yK0g7LyRF7NO1hD%2FJbve%2B%2F9gYl3sCLVCeWoJyO0Y%2FGkK1svFDKKgpyFYaMIxjnMsORCW2JY5jd8YOJbk%2FyAZ7TNPoc5h%2BRwV8FYDIbBukou7HRd%2Ff8j%2BbKFF0R90zBMN6nM5C4EJzQmPnfoghTLbC23Xw08naqkAAAA&sp=SE&sp=SCS&sp=4",
"https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAAFvzloG1uIhBPjWlVC%2BlKLUiNUcvs6hErzw1qSS3WC8lsSRRLyS1KJcBAhiZGJh9GNgTk0tCMnNTSxhEfLISyxL1iwtz9EECxSWJuQXWPgwcJUAtzvkpQBVCEBU5iXnp%2BsElRZl56TB5l9Ti5EKGOgamioKCEgY2IwNDYyNToJHhmXlAaYXA0sQiEG1orGtoAgDaZpl%2BpgAAAA%3D%3D&sp=SE&sp=SCS&sp=4",
"https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAAFvzloG1uIhBPjWlVC%2BlKLUiNUcvs6hErzw1qSS3WC8lsSRRLyS1KJcBAhiZGJh9GNgTk0tCMnNTSxhEfLISyxL1iwtz9EECxSWJuQXWPgwcJUAtzvkpQBVCEBU5iXnp%2BsElRZl56TB5l9Ti5EKGOgamioKCEgY2IwNDY2NToJHBBSBVCoGliUVAZQqGxrqGJgBernVCpgAAAA%3D%3D&sp=SE&sp=SCS&sp=4",
"https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAADWMPQ6CQBCFR4w%2FtbGXC7iIYGWpJY2BC4zshKxhEWYHpfJEXs07uIb4yu99770%2FMHMMG9K90kwD1cqwqCddxTqlUVAVxBbGTAKYZrDAUgpjSWCd3fCBkevq6AecoG2PGSzFT0537Y3VaNTYVFEubJrq35%2FJlR28IBjaVmC%2B38VJevCXeW8tcXjpkb0Wxsk2Tr%2BKCkU0pgAAAA%3D%3D&sp=SE&sp=SCS&sp=4",
"https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAADWLTQ6CMBBGR4w%2Fa%2BNeLmChBlYuNa7YGLnASCekpkVoB2Xlibyad7CG%2BC3f9977AzPvYEOqF8rRQEZox%2BJJV7ZeKGQUJTkL4yYRTAtYYMWltsSwLm74wMR3JvkBz2jbfQFLDsnhroKxGg2DTZ1c2Omm%2Fv9H8lUHL4iGtmWY71KZyTwEJzQmPvfoghTLbCvzL1UDVXGkAAAA&sp=SCI&sp=SCS&sp=6",
"https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAAFvzloG1uIhBPjWlVC%2BlKLUiNUcvs6hErzw1qSS3WC8lsSRRLyS1KJcBAhiZGJh9GNgTk0tCMnNTSxhEfLISyxL1iwtz9EECxSWJuQXWPgwcJUAtzvkpQBVCEBU5iXnp%2BsElRZl56TB5l9Ti5EKGOgamioKCEgY2IwNDEyNToJHhmXlAaYXA0sQiEG1oomtoCgDTFYpMpgAAAA%3D%3D&sp=SCI&sp=SCS&sp=6",
"https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAAFvzloG1uIhBPjWlVC%2BlKLUiNUcvs6hErzw1qSS3WC8lsSRRLyS1KJcBAhiZGJh9GNgTk0tCMnNTSxhEfLISyxL1iwtz9EECxSWJuQXWPgwcJUAtzvkpQBVCEBU5iXnp%2BsElRZl56TB5l9Ti5EKGOgamioKCEgY2IwNDE2NToJHBBSBVCoGliUVAZQqGJrqGpgBX3WZwpgAAAA%3D%3D&sp=SCI&sp=SCS&sp=6",
"https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAADWMPQ6CQBCFR4w%2FtbGXC7iAgcpSSxoDFxjZCcGwCLOzSuWJvJp3cA3xld%2F73nt%2FYGEZdqSd0kwjtaphUU%2B6irFKo6AqiQ1MmQUwz2GFlZSNIYFtfsMHRnZoox%2BwgqY%2F5rAWPzndtTc2k9FiV0eFcNPV%2F%2F5MthrgBcHY9wLLQ5ykaeYvC2cMcXhxyF4Lk3SfZF%2BDeVYGpgAAAA%3D%3D&sp=SCI&sp=SCS&sp=5"
]

URL_TO_TERM = { URLS[0]: "Fall Quarter 13-14", URLS[1]: "Winter Quarter 13-14", URLS[2]: "Spring Quarter 13-14", URLS[3]: "Summer Quarter 13-14",
				URLS[4]: "Fall Quarter 14-15", URLS[5]: "Winter Quarter 14-15", URLS[6]: "Spring Quarter 14-15", URLS[7]: "Summer Quarter 14-15" }

class_name = raw_input("Enter the number for the computer science course: ")
search_val = ">" + class_name + "<"

print "CS" + class_name + " was or will be offered the following terms:"
for url in URLS:
	sock = urllib.urlopen(url)
	htmlSource = sock.read()
	sock.close()
	if htmlSource.find(search_val) > 0:
		print URL_TO_TERM[url]
