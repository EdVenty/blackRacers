import abc
from dataclasses import dataclass
from typing import Any, List, Tuple, Type, Union
import cv2
import numpy as np
from enum import Enum

class HorizontalAlignType(Enum):
    LEFT = 0
    RIGHT = 1
    CENTER = 2

class VerticalAlignType(Enum):
    TOP = 0
    BOTTOM = 1
    MIDDLE = 2

@dataclass
class Vector2:
    x: int
    y: int

@dataclass
class Rect:
    point1: Vector2
    point2: Vector2
    w: Union[int, None] = None
    h: Union[int, None] = None

@dataclass
class UnpositionedRect:
    w: int
    h: int

class GElement:
    def calc(point: Vector2) -> Rect:
        ...
    def blit(frame: np.ndarray, point: Vector2) -> np.ndarray:
        ...

@dataclass
class GText(GElement):
    label: str
    font_face: int = cv2.FONT_HERSHEY_COMPLEX_SMALL
    font_scale: int = 1
    thickness: int = 1
    foreground_color: Union[Tuple[int, int, int], None] = (255, 255, 255)
    background_color: Union[Tuple[int, int, int], None] = None

    def calc(self, point: Vector2) -> Rect:
        (w, h), baseline = cv2.getTextSize(self.label, self.font_face, self.font_scale, self.thickness)
        return Rect(
            point, Vector2(point.x + w, point.y + h + baseline), w, h
        )

    def blit(self, frame: np.ndarray, point: Vector2) -> np.ndarray:
        rect = self.calc(point)
        if self.background_color is not None:
            cv2.rectangle(frame, (point.x, point.y), (rect.point2.x, rect.point2.y), self.background_color, -1)
        if self.foreground_color is not None:
            cv2.putText(frame, self.label, (point.x, point.y + rect.h), self.font_face, self.font_scale, self.foreground_color, self.thickness)
        return frame

@dataclass
class GRect(GElement):
    w: int
    h: int
    color: Tuple[int, int, int]
    thickness: int

    def calc(self, point: Vector2) -> Rect:
        return Rect(
            point, Vector2(point.x + self.w, point.y + self.h), self.w, self.h
        )

    def blit(self, frame: np.ndarray, point: Vector2) -> np.ndarray:
        cv2.rectangle(frame, (point.x, point.y), (point.x + self.w, point.y + self.h), self.color, self.thickness)
        return frame

class GMenu:
    def __init__(self, margin: int = 5) -> None:
        self.elements: list[Type[GElement]] = []
        self.margin = margin

    def text(self, 
        text: str, 
        font_face: int = cv2.FONT_HERSHEY_COMPLEX_SMALL,
        font_scale: int = 1,
        thickness: int = 1,
        foreground_color: Union[Tuple[int, int, int], None] = (255, 255, 255),
        background_color: Union[Tuple[int, int, int], None] = None
        ):
        self.put_element(GText(text, font_face, font_scale, thickness, foreground_color, background_color))

    def rect(self, width: int, height: int, color: Tuple[int, int, int], thickness: int = -1):
        self.put_element(GRect(width, height, color, thickness))

    def put_element(self, element: Type[GElement]):
        self.elements.append(element)

    def calc_max_width(self) -> int:
        return max([e.calc(Vector2(0, 0)).w for e in self.elements])

    def calc_height(self) -> int:
        return sum([e.calc(Vector2(0, 0)).h for e in self.elements])

    def blit(self, 
        frame: np.ndarray, 
        horizontal_align: HorizontalAlignType = HorizontalAlignType.LEFT,
        vertical_align: VerticalAlignType = VerticalAlignType.TOP, 
        screen_size: Tuple[int, int] = (640, 480)
        ) -> np.ndarray:
        max_width = self.calc_max_width()
        height = self.calc_height()
        if horizontal_align == HorizontalAlignType.LEFT:
            margin_left = self.margin
        elif horizontal_align == HorizontalAlignType.RIGHT:
            margin_left = screen_size[0] - max_width - self.margin
        elif horizontal_align == HorizontalAlignType.CENTER:
            margin_left = (screen_size[0] - max_width) // 2
        
        if vertical_align == VerticalAlignType.TOP:
            margin_top = self.margin
        elif vertical_align == VerticalAlignType.BOTTOM:
            margin_top = screen_size[1] - height - self.margin
        elif vertical_align == VerticalAlignType.MIDDLE:
            margin_top = (screen_size[1] - height) // 2

        point = Vector2(margin_left, margin_top)
        for e in self.elements:
            if horizontal_align == HorizontalAlignType.LEFT:
                point = Vector2(margin_left, point.y)
            elif horizontal_align == HorizontalAlignType.RIGHT:
                point = Vector2(margin_left + max_width - rect.w, point.y)
            elif horizontal_align == HorizontalAlignType.CENTER:
                point = Vector2(margin_left + (max_width - rect.w) // 2, point.y)
            e.blit(frame, point)
            rect = e.calc(point)
        self.elements.clear()
        return frame 