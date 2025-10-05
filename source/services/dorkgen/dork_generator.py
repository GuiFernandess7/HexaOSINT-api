from abc import ABC, abstractmethod



class DorkingStrategy(ABC):
    @abstractmethod
    def get_dork(self, target_name: str) -> str:
        pass


class SocialDorking(DorkingStrategy):
    def get_dork(self, target_name: str) -> str:
        parts = [
            f'site:facebook.com "{target_name}"',
            f'site:twitter.com "{target_name}"',
        ]
        return " OR ".join(parts)


class FilesDorking(DorkingStrategy):
    def get_dork(self, target_name: str) -> str:
        parts = [
            f'"{target_name}" filetype:pdf',
            f'"{target_name}" filetype:xls',
        ]
        return " OR ".join(parts)


class DorkingFactory:
    strategies = {
        "social": SocialDorking,
        "files": FilesDorking,
    }

    @classmethod
    def get_strategy(cls, category: str) -> DorkingStrategy:
        strat_cls = cls.strategies.get(category)
        if not strat_cls:
            raise ValueError(f"Categoria desconhecida: {category}")
        return strat_cls()


def build_combined_dork(target_name: str, categories: list[str]) -> str:
    blocks = []
    for cat in categories:
        strat = DorkingFactory.get_strategy(cat)
        blocks.append(strat.get_dork(target_name))
    return " AND ".join(blocks)
