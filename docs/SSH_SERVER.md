# SSH w Mara_OS (Debian 13)

Mara_OS dostarcza instalator serwera OpenSSH uruchamianego automatycznie przy starcie systemu.

## Instalacja na docelowym Debianie 13

```bash
sudo bash scripts/install-ssh-server.sh
```

Skrypt instaluje `openssh-server`, dodaje `/etc/ssh/sshd_config.d/60-mara-os.conf` z `PermitRootLogin no`, sprawdza konfigurację przez `sshd -t`, włącza usługę `ssh.service` i uruchamia ją. Nie modyfikuje reguł zapory ani routera.

## Połączenie

Na komputerze Mara_OS:

```bash
hostname -I
systemctl status ssh
```

Z innego komputera:

```bash
ssh NAZWA_UZYTKOWNIKA@IP_MARA_OS
```

Przesyłanie plików: `sftp NAZWA_UZYTKOWNIKA@IP_MARA_OS`.

## Bezpieczeństwo

Domyślnie zdalne logowanie root jest wyłączone. Uwierzytelnianie zwykłych użytkowników zależy od konfiguracji systemowej; przed dostępem z internetu zaleca się klucze SSH, zaporę i VPN. Wyłączenie logowania hasłem powinno nastąpić dopiero po sprawdzeniu dostępu kluczem. Nie przyznajemy agentom AI automatycznych uprawnień SSH ani root.

**Stan:** pliki instalacyjne są w repozytorium. Na rzeczywistym Debianie 13 instalator musi zostać uruchomiony; nie potwierdzono aktywnej usługi SSH.
