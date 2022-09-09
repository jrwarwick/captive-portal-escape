# captive-portal-escape
Utility to automate re-accept and confirm terms of WiFi captive portals so as to reduce interruptions to network connectivity

## Originating Scenario
When you have a super neato voice-operated digital assistant in your office, 
but your net admin only offers guest wifi for that kind of thing
but the guest wifi has periodic disconnect-and-reaffirm-your-compliance captive portal business all over that wifi.
This is just a little something to help that voice-operated digital assistant keep /itself/ connected.

## Installation
```
cp captive_portal_escape.py /opt/mycroft/
deactivate
pip install bs4
cp captive-portal-escape.service /etc/systemd/system
cp captive-portal-escape.timer /etc/systemd/system
systemctl enable captive-portal-escape.timer
```
