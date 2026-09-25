# Quake II Map to Unreal Engine 5

Convert Quake II-style `.map` files into Unreal Engine 5 `.t3d` scenes.

This project exports brush-based map geometry, texture coordinates, lights, and point entities to UE5 T3D format, making it easier to inspect or reuse classic level data in Unreal Engine 5.

> A legacy FBX exporter (`map_to_fbx.py` + `id_map.py`) is still present but requires the Autodesk FBX SDK. The recommended path is `QUAKE2_MAP_2_T3D.py`.

## Features

- Parse Quake II / QuakeEd4-compatible `.map` files
- Export brush geometry as polygonal meshes
- Generate per-polygon UV coordinates from Quake `texdef` data
- Write `Texture=` material references using a configurable mapping file
- Convert lights, player starts, monsters, triggers, items, and notes to UE5 actors
- Organize actors into UE5 folders (`Quake2/Geometry`, `Quake2/Lights`, etc.)
- Export a conversion log alongside the `.t3d` file

## Current Limitations

- Internal or non-visible faces are not yet removed
- Material mapping requires a user-supplied config file
- Support may vary depending on map editor output and texture archive layout

## Requirements

- Python 3.8 or newer
- Pillow 2.8.1 or newer (for the legacy FBX exporter)
- A QuakeEd4-compatible `.map` file

Supported editors include:

- Embrace
- QE4
- QERadiant
- WorldCraft

## Installation

1. Install Python.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Clone this repository:

   ```bash
   git clone https://github.com/AlleyKatPr0/Quake2UE.git
   cd Quake2UE
   ```

## Usage

Run the T3D converter with a source map file:

```bash
python QUAKE2_MAP_2_T3D.py input.map
```

Specify an output file and grid snap size:

```bash
python QUAKE2_MAP_2_T3D.py input.map output.t3d --grid 2.54
```

Use a material mapping config file to map Quake texture names to UE5 material paths:

```bash
python QUAKE2_MAP_2_T3D.py input.map output.t3d --materials materials.cfg
```

The config file is a simple key-value list:

```text
base_floor=/Game/Materials/BaseFloor
base_wall=/Game/Materials/BaseWall
```

Disable the exit pause for scripted workflows:

```bash
python QUAKE2_MAP_2_T3D.py input.map output.t3d --no-pause
```

To import into UE5:

1. Open the generated `.t3d` file in a text editor.
2. Select all and copy.
3. Paste into the UE5 viewport.

## Testing

Run the smoke tests with Python's built-in unittest runner:

```bash
python -m unittest discover -s tests -v
```

## Example Output

Example export: Prague North Quarter from *Vampire: The Masquerade – Redemption*.

![Example export](http://s22.postimg.org/y464wfy01/north_district_night.jpg)

## How It Works

`QUAKE2_MAP_2_T3D.py` parses map entities and brush planes, reconstructs brush vertices by intersecting planes, triangulates each face, and writes UE5 T3D actor definitions.

The legacy FBX path was built using the Quake II QE4 source code as a reference for parsing map geometry.

## Roadmap

- Remove faces that are not visible from inside the playable space
- Improve texture and material handling
- Add better validation and error reporting
- Support target/targetname relationships and func_group grouping

## Contributing

Issues and pull requests are welcome.

## License

Add a license section here if the repository includes one.
