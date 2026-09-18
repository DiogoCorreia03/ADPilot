from adpilot_mcp.services.recon import (
    build_curl_command,
    build_nmap_command,
    build_nslookup_command,
)
from adpilot_mcp.services.ad_enum import (
    build_smbclient_command,
    build_ldapsearch_command,
    build_netexec_command,
    build_getadusers_command,
    build_lookupsid_command,
)
from adpilot_mcp.services.kerberos import (
    build_getnpusers_command,
    build_getuserspns_command,
    build_kerbrute_command,
    build_ticketer_command,
)
from adpilot_mcp.services.lateral import (
    build_secretsdump_command,
    build_wmiexec_command,
    build_certipy_command,
    build_addcomputer_command,
    build_dnstool_command,
)



def test_curl_command_builder():
    cmd = build_curl_command(
        url="http://10.10.10.10/login",
        method="POST",
        headers="Authorization: Bearer test",
        data="user=admin",
        extra_args="--insecure",
    )
    assert "curl -X POST 'http://10.10.10.10/login'" in cmd
    assert '-H "Authorization: Bearer test"' in cmd
    assert "-d 'user=admin'" in cmd
    assert "--insecure" in cmd


def test_nmap_command_builder():
    cmd = build_nmap_command(target="192.168.1.0/24", flags="-p 445,389 -sV")
    assert cmd == "nmap -p 445,389 -sV 192.168.1.0/24"


def test_nslookup_command_builder():
    cmd = build_nslookup_command(
        query="corp.local", record_type="SRV", extra_args="_ldap._tcp.dc._msdcs.corp.local"
    )
    assert "nslookup -type=SRV" in cmd
    assert "_ldap._tcp.dc._msdcs.corp.local" in cmd
    assert "corp.local" in cmd


def test_smbclient_command_builder():
    cmd = build_smbclient_command(
        target="10.10.10.5",
        service="C$",
        username="administrator",
        password="Password123!",
        command="dir; get flag.txt",
    )
    assert "smbclient //10.10.10.5/C$" in cmd
    assert "-U 'administrator%Password123!'" in cmd
    assert "-c 'dir; get flag.txt; exit'" in cmd


def test_ldapsearch_command_builder():
    cmd = build_ldapsearch_command(
        target="dc01.corp.local",
        base_dn="DC=corp,DC=local",
        search_filter="(objectCategory=user)",
        attributes="sAMAccountName mail",
        bind_dn="CN=admin,CN=Users,DC=corp,DC=local",
        password="Pass",
        use_ssl=True,
    )
    assert "ldaps://dc01.corp.local" in cmd
    assert "-b 'DC=corp,DC=local'" in cmd
    assert "'(objectCategory=user)'" in cmd
    assert "sAMAccountName mail" in cmd
    assert "-D 'CN=admin,CN=Users,DC=corp,DC=local'" in cmd
    assert "-w 'Pass'" in cmd


def test_netexec_command_builder():
    cmd = build_netexec_command(
        protocol="smb",
        target="192.168.1.10",
        username="user1",
        password="pwd",
        extra_args="--shares",
    )
    assert "nxc smb 192.168.1.10" in cmd
    assert "-u 'user1'" in cmd
    assert "-p 'pwd'" in cmd
    assert "--shares" in cmd


def test_kerbrute_command_builder_validation():
    # Test valid userenum
    cmd, err = build_kerbrute_command(
        domain="corp.local",
        dc_ip="10.10.10.1",
        mode="userenum",
        usersfile="/tmp/users.txt",
    )
    assert err is None
    assert cmd is not None
    assert "/root/kerbrute userenum '/tmp/users.txt' -d corp.local --dc 10.10.10.1" in cmd

    # Test rockyou block
    cmd, err = build_kerbrute_command(
        domain="corp.local",
        dc_ip="10.10.10.1",
        mode="userenum",
        usersfile="/usr/share/wordlists/rockyou.txt",
    )
    assert err is not None
    assert "rockyou.txt" in err


def test_secretsdump_command_builder():
    cmd = build_secretsdump_command(
        domain="corp.local",
        target="10.10.10.1",
        username="administrator",
        password="Password123!",
        just_dc=True,
    )
    assert "secretsdump.py corp.local/administrator:Password123!@10.10.10.1" in cmd
    assert "-just-dc" in cmd


def test_certipy_command_builder():
    cmd, err = build_certipy_command(
        action="find",
        domain="corp.local",
        username="auditor",
        password="Password1!",
        dc_ip="10.10.10.1",
    )
    assert err is None
    assert cmd is not None
    assert "certipy find" in cmd
    assert "-u 'auditor@corp.local'" in cmd
    assert "-vulnerable" in cmd


def test_netexec_command_builder_none_extra_args():
    # Calling netexec with extra_args=None should not crash with TypeError
    cmd = build_netexec_command(
        protocol="smb",
        target="192.168.1.10",
        username="user1",
        password="pwd",
        extra_args=None,
    )
    assert "nxc smb 192.168.1.10" in cmd
    assert "-u 'user1'" in cmd


def test_getuserspns_command_builder_hashes_without_password():
    cmd = build_getuserspns_command(
        domain="corp.local",
        username="targetuser",
        output_file="/tmp/spns.hash",
        password=None,
        hash_="aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0",
    )
    assert "-hashes aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0" in cmd
    assert "-no-pass" in cmd


def test_getuserspns_command_builder_kerberos_with_password():
    cmd = build_getuserspns_command(
        domain="corp.local",
        username="targetuser",
        output_file="/tmp/spns.hash",
        password="SecretPassword1!",
        use_kerberos=True,
    )
    assert ":SecretPassword1!" in cmd
    assert "-k" in cmd


def test_dnstool_command_builder_password_quoting():
    cmd = build_dnstool_command(
        hostname="dc01.corp.local",
        action="add",
        username="corp\\admin",
        password="P@ss;calc&id",
        record="test.corp.local",
        record_data="192.168.1.50",
    )
    assert "-p 'P@ss;calc&id'" in cmd

