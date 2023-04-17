from typing import List, Literal
from datetime import datetime
from pydantic import BaseModel, DirectoryPath


class Card(BaseModel):
    card_id: str
    stage_offsets: List[int]
    acquisition_time: datetime
    subdir_path: str
    image_format: Literal["jpeg", "png", "tiff", "raw"]


class Storage(BaseModel):
    root_filesystem: DirectoryPath
    cards: List[Card] = []

    @classmethod
    def open(cls, root_filesystem: DirectoryPath):
        listing_file = root_filesystem / "listing.json"
        if listing_file.exists():
            return cls.parse_file(listing_file)
        else:
            return Storage(root_filesystem=root_filesystem, cards=[])

    def save(self):
        with (self.root_filesystem / "listing.json").open("w+") as f:
            f.write(self.json())

    def add_card(self, card: Card):
        self.cards.append(card)
        self.save()
