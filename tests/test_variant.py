from lib.variant import Variant


class TestVariant:
    """Test the Variant class."""
    def test_constructor(self):
        variant = Variant('pt-BR')
        assert variant.lang == 'pt'
        assert variant.country == 'BR'
        assert variant.agreement is None
        assert variant.pretty == 'Portuguese'
        assert variant.hyphenated == 'pt-BR'
        assert variant.underscored == 'pt_BR'
        assert variant.dict().endswith('pt-BR.dict')
        assert variant.dic().endswith('pt_BR.dic')
        assert variant.aff().endswith('pt_BR.aff')
        assert variant.info('source').endswith('pt-BR.info')
        assert variant.freq().endswith('pt_BR_wordlist.xml')

    def test_constructor_with_agreement(self):
        variant = Variant('pt-PT-45')
        assert variant.lang == 'pt'
        assert variant.country == 'PT'
        assert variant.agreement == '45'
