# Upchuck

Upchuck is a desktop dice roller with transparent, vector-drawn polyhedral dice and a rigid-body simulation.
Drag any die to gather and throw the group. Right-click or double-click a die to change the dice and their appearance
(a spinning preview die beside the options window shows the result);
press Escape to close the application.

Run from the Kōtuku repository root with an installed Origo executable:

```bash
build/agents-install/origo projects/upchuck/dice.tiri --log-warning
```

Choose the number of dice, their sides and colours:

```bash
build/agents-install/origo projects/upchuck/dice.tiri dice=4 sides=4,6,12,20 colours=white,red,blue,green --log-warning
```

Set the font family for number labels with `font` (default: `sans-serif`). Use `face=num` for numbered D6 faces;
other dice always use numbers. Quote family names containing spaces. Comma-separated families provide fallbacks:

```bash
build/agents-install/origo projects/upchuck/dice.tiri face=num font="Noto Sans,sans-serif" --log-warning
```

Upchuck supports D4, D6, D8, D10, D12 and D20 dice. Run with `help` to see all options:

```bash
build/agents-install/origo projects/upchuck/dice.tiri help --log-warning
```
