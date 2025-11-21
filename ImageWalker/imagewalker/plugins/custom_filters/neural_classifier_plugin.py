import os
from dataclasses import dataclass
from typing import Any, Dict

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as T
from PIL import Image

from imagewalker.plugins.registry import PluginRegistry
from imagewalker.domain.file_system_domain import File
from imagewalker.filters.filters import Filter
from imagewalker.plugins.interface import (
    BaseFilterPlugin,
    PluginConfig,
    template_plugin,
)


class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1, downsample=None):
        super(ResidualBlock, self).__init__()

        self.conv1 = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=3,
            stride=stride,
            padding=1,
            bias=False,
        )
        self.bn1 = nn.BatchNorm2d(out_channels)

        self.conv2 = nn.Conv2d(
            out_channels,
            out_channels,
            kernel_size=3,
            stride=1,
            padding=1,
            bias=False,
        )
        self.bn2 = nn.BatchNorm2d(out_channels)

        self.bn3 = nn.BatchNorm2d(out_channels)
        self.conv3 = nn.Conv2d(
            out_channels,
            out_channels,
            kernel_size=3,
            stride=1,
            padding=1,
            bias=False,
        )

        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = F.relu(out, inplace=True)

        out = self.conv2(out)
        out = self.bn2(out)
        out = F.relu(out, inplace=True)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            identity = self.downsample(x)

        out += identity
        out = F.relu(out, inplace=True)

        return out


class CNN(nn.Module):
    def __init__(self, num_classes=6, use_bottleneck=False, dropout_rate=0.3):
        super(CNN, self).__init__()

        self.use_bottleneck = use_bottleneck
        self.in_channels = 64

        self.conv1 = nn.Conv2d(
            3,
            64,
            kernel_size=7,
            stride=2,
            padding=3,
            bias=False,
        )
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(
            kernel_size=3,
            stride=2,
            padding=1,
        )
        self.dropout = nn.Dropout(0.1)

        self.layer1 = self._make_layer(64, 64, blocks=2, stride=1)
        self.layer2 = self._make_layer(64, 128, blocks=2, stride=2)
        self.layer3 = self._make_layer(128, 256, blocks=2, stride=2)
        self.layer4 = self._make_layer(256, 512, blocks=2, stride=2)
        self.layer5 = self._make_layer(512, 1024, blocks=2, stride=2)

        self.classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Flatten(),
            nn.Linear(1024, 2048),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate / 1.75),
            nn.Linear(2048, num_classes),
        )
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))

    def _make_layer(self, in_channels, out_channels, blocks, stride):
        """Для обычных Residual блоков"""
        downsample = None

        if stride != 1 or in_channels != out_channels:
            downsample = nn.Sequential(
                nn.Conv2d(
                    in_channels,
                    out_channels,
                    kernel_size=1,
                    stride=stride,
                    bias=False,
                ),
                nn.BatchNorm2d(out_channels),
            )

        layers = []
        layers.append(
            ResidualBlock(
                in_channels,
                out_channels,
                stride,
                downsample,
            )
        )

        for _ in range(1, blocks):
            layers.append(
                ResidualBlock(
                    out_channels,
                    out_channels,
                )
            )

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.layer5(x)
        x = self.dropout(x)

        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)

        return x


def get_transforms(img_size=150, is_train=True):
    if is_train:
        return T.Compose(
            [
                T.Resize((img_size, img_size)),
                T.RandomHorizontalFlip(0.5),
                T.RandomVerticalFlip(0.25),
                T.RandomRotation(15),
                T.ColorJitter(
                    brightness=0.25, contrast=0.25, saturation=0.25, hue=0.15
                ),
                T.RandomAffine(
                    degrees=(0, 15), translate=(0.15, 0.15), scale=(0.85, 1.15)
                ),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )
    else:
        return T.Compose(
            [
                T.Resize((img_size, img_size)),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )


@dataclass
class NeuralClassifierConfig(PluginConfig):
    """Configuration for neural network image classification plugin.

    Attributes:
        confidence_threshold: Minimum confidence threshold for classification (0.0-1.0).
        process_non_images: Whether to process non-image files.
    """

    confidence_threshold: float = 0.8
    process_non_images: bool = False


class NeuralClassifierFilter(Filter):
    """Filter that categorizes images using neural network classification."""

    def __init__(
        self,
        confidence_threshold: float = 0.8,
        process_non_images: bool = False,
        order: int = 0,
    ):
        self.confidence_threshold = confidence_threshold
        self.process_non_images = process_non_images
        self._order = order

        # Инициализация модели
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.classes = None
        self.transform = None
        self.classes = ["buildings", "forest", "glacier", "mountain", "sea", "street"]

        # Поддерживаемые расширения изображений
        self.image_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".tiff",
            ".webp",
            ".tif",
        }

        self._initialize_model()

    def _initialize_model(self):
        """Инициализация модели нейросети"""
        try:
            print(f"NeuralClassifier: Initializing model on {self.device}")

            # Загрузка модели
            self.model = CNN(num_classes=len(self.classes))

            model_path = "imagewalker\\plugins\\custom_filters\\best_model.pth"

            if os.path.exists(model_path):
                checkpoint = torch.load(model_path, map_location=self.device)
                self.model.load_state_dict(checkpoint["model_state_dict"])
                self.model.to(self.device)
                self.model.eval()
                print("NeuralClassifier: Model loaded successfully!")
            else:
                print(f"NeuralClassifier: Model not found at {model_path}")
                self.model = None
                return

            # Подготовка трансформаций
            self.transform = get_transforms(150, is_train=False)

        except Exception as e:
            print(f"NeuralClassifier: Model initialization failed: {e}")
            self.model = None

    def _predict_image(self, file_path):
        """Предсказание для одного изображения"""
        if self.model is None:
            return None, 0.0

        try:
            image = Image.open(file_path).convert("RGB")
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                output = self.model(image_tensor)
                probabilities = torch.softmax(output, dim=1)
                confidence, predicted = torch.max(probabilities, 1)

            return predicted.item(), confidence.item()

        except Exception as e:
            print(f"NeuralClassifier: Error processing {file_path}: {e}")
            return None, 0.0

    def get_category(self, file: "File") -> str:
        """Определение категории для файла на основе классификации нейросети"""
        file_ext = file.extension.lower()

        # Проверяем, является ли файл изображением
        if file_ext not in self.image_extensions:
            if self.process_non_images:
                return "non_images"
            else:
                return "other_files"

        # Если модель не загружена, возвращаем в папку для ошибок
        if self.model is None:
            return "model_not_loaded"

        # Классифицируем изображение
        class_id, confidence = self._predict_image(file.path)

        if class_id is None:
            return "classification_error"

        class_name = (
            self.classes[class_id] if class_id < len(self.classes) else "unknown"
        )

        # Проверяем порог уверенности
        if confidence < self.confidence_threshold:
            return f"low_confidence_{class_name}"

        return class_name

    def get_order(self) -> int:
        return self._order

    def get_name(self) -> str:
        return "neural_classifier"

    def is_applicable(self, file: "File") -> bool:
        """Фильтр применим ко всем файлам, но обрабатывает только изображения"""
        return True


@template_plugin
@PluginRegistry.register("neural_classifier")
class NeuralClassifierPlugin(BaseFilterPlugin):
    """Plugin for grouping images by neural network classification."""

    def create_filter(self, config: Dict[str, Any]):
        return NeuralClassifierFilter(
            order=config.get("order", 0),
            confidence_threshold=config.get("confidence_threshold", 0.8),
            process_non_images=config.get("process_non_images", False),
        )

    @classmethod
    def get_config_class(cls):
        return NeuralClassifierConfig

    def get_filter_info(self):
        """Информация о фильтре"""
        return {
            "name": "neural_classifier",
            "description": "Classifies images using neural network (forest, glacier, mountain, sea, streets, buildings)",
            "version": "1.0.0",
            "author": "Delshi Delman",
            "supported_file_types": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"],
        }
