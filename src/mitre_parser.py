"""Parser and indexing utility for MITRE ATT&CK Enterprise Matrix."""

from typing import Dict, List, Optional
import json
from pathlib import Path


class MitreTechniqueParser:
    """Parses and formats MITRE ATT&CK enterprise techniques for RAG indexing."""

    def __init__(self, raw_data_path: Optional[Path] = None):
        self.raw_data_path = raw_data_path

    @staticmethod
    def parse_technique_object(stix_obj: Dict) -> Optional[Dict]:
        """Convert a STIX attack-pattern object into a clean RAG-ready document."""
        if stix_obj.get("type") != "attack-pattern":
            return None

        ext_refs = stix_obj.get("external_references", [])
        technique_id = None
        for ref in ext_refs:
            if ref.get("source_name") == "mitre-attack":
                technique_id = ref.get("external_id")
                break

        if not technique_id:
            return None

        return {
            "technique_id": technique_id,
            "name": stix_obj.get("name", "Unknown Technique"),
            "description": stix_obj.get("description", ""),
            "platforms": stix_obj.get("x_mitre_platforms", []),
            "tactics": [
                phase.get("phase_name")
                for phase in stix_obj.get("kill_chain_phases", [])
            ],
            "url": f"https://attack.mitre.org/techniques/{technique_id}",
        }

    def format_for_indexing(self, techniques: List[Dict]) -> List[Dict[str, str]]:
        """Format techniques into document chunks with clear metadata tags."""
        documents = []
        for tech in techniques:
            content = (
                f"MITRE ATT&CK Technique: {tech['name']} ({tech['technique_id']})\n"
                f"Tactics: {', '.join(tech['tactics'])}\n"
                f"Platforms: {', '.join(tech['platforms'])}\n\n"
                f"Description:\n{tech['description']}"
            )
            documents.append({
                "page_content": content,
                "metadata": {
                    "source": f"MITRE-{tech['technique_id']}",
                    "technique_id": tech['technique_id'],
                    "type": "mitre_technique",
                }
            })
        return documents
