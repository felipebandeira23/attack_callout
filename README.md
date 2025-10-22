## Bot attack_callout.py


Este bot detecta mensagens no chat com marcações de setor (como `D4`, `E5`, etc.) e automaticamente envia uma chamada de ataque para o time, facilitando a comunicação do comandante com os jogadores.


### Funcionalidade
- Detecta mensagens como `!atk D6` ou `!atacar H3` no chat.
- Envia uma mensagem de administrador visível para todo o time com o setor marcado como alvo.
- Pode ser usado para facilitar callouts rápidos durante partidas intensas.


### Instalação
1. Copie o arquivo `attack_callout.py` para a pasta `custom_tools/` do seu CRCON:
```bash
cp attack_callout.py custom_tools/
```


2. No `hooks.py`, registre o gancho:
```python
import custom_tools.attack_callout as attack_callout


@on_chat
def attack_callout_chat(rcon, log):
attack_callout.on_chat_attack_callout(rcon, log)
```


3. Reinicie o CRCON:
```bash
./restart.sh
```


### Comando no jogo
Comandante ou líder de esquadrão digita:
```
!atk G5
```
ou
```
!atacar C3
```


O time receberá uma mensagem como:
```
ATENÇÃO: Ataque coordenado em G5! Todos para o setor!
```


## Licença
MIT
