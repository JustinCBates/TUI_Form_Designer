from pathlib import Path
from typing import Dict, Any
import yaml


class LayoutPreprocessor:
    """
    Expands 'sublayout' references by inlining the referenced layout's steps.
    """

    def __init__(self, layouts_dir: Path):
        self.layouts_dir = Path(layouts_dir)

    def reconstruct_virtual_layout(
        self, layout_path: Path, save_virtual: bool = False, output_path: Path = None
    ) -> Dict[str, Any]:
        with open(layout_path, "r") as f:
            data = yaml.safe_load(f) or {}

        steps = data.get("steps", [])
        expanded_steps = []
        for step in steps:
            sub = step.get("sublayout")
            if sub:
                sub_path = (layout_path.parent / sub).resolve()
                with open(sub_path, "r") as sf:
                    sub_data = yaml.safe_load(sf) or {}
                
                    # Inject header step for sublayout if it has title/description
                    sub_title = sub_data.get("title")
                    sub_desc = sub_data.get("description")
                    if sub_title or sub_desc:
                        header_step = {
                            "id": f"_header_{sub_data.get('layout_id', 'sublayout')}",
                            "type": "info",
                            "title": sub_title or "Section",
                            "message": sub_desc or "",
                        }
                        expanded_steps.append(header_step)
                
                sub_steps = sub_data.get("steps", [])
                expanded_steps.extend(sub_steps)
            else:
                expanded_steps.append(step)

        data["steps"] = expanded_steps

        if save_virtual and output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as out:
                yaml.safe_dump(data, out, default_flow_style=False, sort_keys=False)

        return data
