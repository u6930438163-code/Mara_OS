# SSH w Mara_OS (Debian 13)

Mara_OS dostarcza instalator serwera OpenSSH uruchamianego automatycznie przy starcie systemu.

## Instalacja na docelowym Debianie 13

```bash
sudo bash scripts/install-ssh-server.sh
```

Skrypt instaluje `openssh-server`, dodaje `/etc/ssh/sshd_config.d/60-mara-os.conf` z `PermitRootLogin yes`, `PasswordAuthentication yes` i `AllowUsers root`, sprawdza konfigurację przez `sshd -t`, włącza usługę `ssh.service` i uruchamia ją. Nie modyfikuje reguł zapory ani routera.

## Połączenie

Na komputerze Mara_OS:

```bash
hostname -I
systemctl status ssh
```

Z innego komputera:

```bash
ssh root@IP_MARA_OS
```

Przesyłanie plików: `sftp root@IP_MARA_OS`.

## Bezpieczeństwo

Na wyraźne życzenie właściciela SSH dopuszcza tylko użytkownika `root` z hasłem ustawianym interaktywnie poleceniem `passwd root` podczas instalacji. Hasło nie trafia do repozytorium. Jest to konfiguracja podwyższonego ryzyka: zalecane są VPN, ograniczenie adresów IP zaporą oraz ochrona przed próbami logowania. Nie przyznajemy agentom AI automatycznych uprawnień SSH ani root.

**Stan:** pliki instalacyjne są w repozytorium. Na rzeczywistym Debianie 13 instalator musi zostać uruchomiony; nie potwierdzono aktywnej usługi SSH.
