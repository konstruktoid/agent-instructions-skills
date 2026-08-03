# Credentials in shell scripts

Shell makes secrets visible in more places than most languages: the process table, the trace
output, the shell history, the log the scheduler mails, and the transcript someone pastes into an
issue.

## Where a secret must never appear

- **A command-line argument.** Every user on the host can read it from `ps` and `/proc/<pid>/cmdline`
  while the command runs. This includes `mysql -p"${pass}"`, `curl -u "user:${pass}"`,
  `docker login -p`, and any tool taking `--token`.
- **A script, a repository file, or a container image layer.** A credential in git history is
  compromised for as long as the history exists.
- **A log, a CI transcript, or an error message.** Including through `set -x` and through an `ERR`
  trap that prints variables.
- **A world-readable or group-readable file.** Mode `0600`, owned by the account that uses it.

## Getting a secret into a command safely

Ordered from best to acceptable:

1. **A secret manager or the platform's credential mechanism**: `systemd` `LoadCredential=`, the CI
   system's masked secrets, `vault read`, `aws secretsmanager get-secret-value`, `pass`, `gpg -d`.
2. **Standard input**: `docker login --password-stdin`, `gpg --passphrase-fd 0`,
   `openssl … -passin stdin`, `ssh-add` reading from a prompt.
3. **A file with mode 0600, referenced by path**: `curl --netrc-file`, `curl -H @headerfile`,
   `mysql --defaults-extra-file`, `restic --password-file`, `borg BORG_PASSCOMMAND`.
4. **An environment variable**, where the tool supports one and the alternatives do not apply. It
   stays out of `ps`, but it is inherited by every child process, appears in
   `/proc/<pid>/environ`, and is captured by crash handlers and by `docker inspect`.

Reading one interactively:

```bash
read -r -s -p 'Passphrase: ' passphrase
printf '\n' >&2
```

`-s` suppresses echo; the explicit newline keeps the prompt from running into the next output. If
the script can be interrupted while echo is off, restore it from the trap: `stty echo`.

Loading one from a file, with the permission check from
[filesystem.md](filesystem.md):

```bash
require_secure_file "${credentials_file}"
# shellcheck source=/dev/null
source "${credentials_file}"        # the file is code: it must be trusted and mode 0600
```

Sourcing is convenient and executes the file. Where the file comes from anywhere less trusted than
the script itself, parse the values instead of sourcing them.

## Tracing and debugging

`set -x` prints every command with its arguments expanded, so it prints secrets. In CI, where the
log may be public, this is the most common way a credential escapes.

```bash
set +x                       # disable around the sensitive section
authenticate "${token}"
set -x                       # restore only if it was on
```

Better, keep the trace away from the log entirely: `exec {BASH_XTRACEFD}>/var/log/script.trace`
sends `xtrace` output to a file instead of stderr. `PS4` is expanded on every traced command, so
never build it from data.

An `ERR` or `DEBUG` trap that prints `BASH_COMMAND` prints the expanded command, secrets included.
Print the line number and the function name instead.

Redact deliberately when a value must be logged at all:

```bash
printf 'authenticating with token %s…\n' "${token:0:4}" >&2
```

## Generating secrets

```bash
openssl rand -base64 32
head -c 32 /dev/urandom | base64
tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 32; printf '\n'
```

Use `/dev/urandom` or `openssl rand`. Never `$RANDOM`, which is a 15-bit value from a predictable
generator, and never a value derived from the time, the PID, or a hash of a hostname. Where a
password policy requires a character class, generate more entropy and filter, rather than
constructing the value from small pieces.

Shell has no constant-time comparison. A script that compares a submitted token against a stored
one is doing authentication in the wrong place: move that to a program that can do it properly.

## Containing the damage

- Assume a secret that reached a log, a transcript, a `ps` listing, or git history is compromised.
  Rotate it. Removing the line afterwards does not undo the exposure.
- `shred` does not reliably erase a file on a journaling or copy-on-write filesystem, on flash
  storage, or on any snapshotted volume. Keep secrets out of files that outlive the run instead:
  `mktemp` with `umask 077`, removed by the `EXIT` trap.
- Interactive shells record commands in `HISTFILE`. Do not instruct a user to paste a secret onto a
  command line; have the script prompt for it, or read it from a file.
- Add credential filenames to `.gitignore` in the same change that introduces them, and never
  commit an example file containing a real value.

## Output the repository keeps

Anything a script captures and commits, such as a transcript, a fixture, or generated
documentation, must be normalized first: no tokens, no home-directory paths, no usernames, no
uids, no hostnames, no internal IP addresses, no real email addresses. Use placeholders
(`/path/to/project`, `user@example.com`, RFC 5737 addresses) and derive real values at runtime
(`$HOME`, `id -un`, `hostname`) instead of writing them into the file.
