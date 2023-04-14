from typing import List, Literal
from datetime import datetime
from pydantic import BaseModel, DirectoryPath


class Card(BaseModel):
    card_id: int
    num_images: int
    acquisition_time: datetime
    subdir_path: DirectoryPath
    image_format: Literal["jpeg", "png", "tiff", "raw"]


class Storage(BaseModel):
    root_filesystem: DirectoryPath
    cards: List[Card] = []

    @classmethod
    def open(cls, root_filesystem: DirectoryPath):
        cls.parse_file(root_filesystem / "listing.json")

    def save(self):
        with (self.root_filesystem / "listing.json").open("w+") as f:
            f.write(self.json())

    def add_card(self, card: Card):
        self.cards.append(card)
        self.save()
