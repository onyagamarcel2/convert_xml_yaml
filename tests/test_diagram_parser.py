"""
Tests pour le module diagram_parser.py
"""

import unittest
from src.utils.diagram_parser import DiagramParser, COMPONENT_TYPES, DATA_TYPES, COMMUNICATION_PROTOCOLS

class TestDiagramParser(unittest.TestCase):
    """Tests pour la classe DiagramParser"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        # Exemple de diagramme DrawIO minimal
        self.minimal_drawio = """<?xml version="1.0" encoding="UTF-8"?>
        <mxfile>
            <diagram>
                <mxGraphModel>
                    <root>
                        <mxCell id="0"/>
                        <mxCell id="1" parent="0"/>
                        <mxCell id="2" value="Web App" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
                            <mxGeometry x="120" y="120" width="120" height="60" as="geometry"/>
                        </mxCell>
                        <mxCell id="3" value="Database" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;" vertex="1" parent="1">
                            <mxGeometry x="320" y="120" width="60" height="80" as="geometry"/>
                        </mxCell>
                        <mxCell id="4" value="" style="endArrow=classic;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="2" target="3">
                            <mxGeometry width="50" height="50" relative="1" as="geometry"/>
                        </mxCell>
                    </root>
                </mxGraphModel>
            </diagram>
        </mxfile>"""

        # Exemple de diagramme avec des menaces
        self.threat_drawio = """<?xml version="1.0" encoding="UTF-8"?>
        <mxfile>
            <diagram>
                <mxGraphModel>
                    <root>
                        <mxCell id="0"/>
                        <mxCell id="1" parent="0"/>
                        <mxCell id="2" value="API Gateway" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
                            <mxGeometry x="120" y="120" width="120" height="60" as="geometry"/>
                        </mxCell>
                        <mxCell id="3" value="SQL Injection" style="ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
                            <mxGeometry x="280" y="120" width="120" height="60" as="geometry"/>
                        </mxCell>
                        <mxCell id="4" value="" style="endArrow=classic;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="2" target="3">
                            <mxGeometry width="50" height="50" relative="1" as="geometry"/>
                        </mxCell>
                    </root>
                </mxGraphModel>
            </diagram>
        </mxfile>"""

    def test_detect_diagram_type(self):
        """Test de la détection du type de diagramme"""
        parser = DiagramParser(self.minimal_drawio)
        self.assertEqual(parser.diagram_type, 'drawio')

    def test_extract_cells(self):
        """Test de l'extraction des cellules"""
        parser = DiagramParser(self.minimal_drawio)
        cells = parser._extract_cells()
        self.assertEqual(len(cells), 4)  # 4 cellules dans le diagramme minimal
        self.assertTrue(any(cell['id'] == '2' for cell in cells))  # Vérifie la présence de la Web App

    def test_determine_component_type(self):
        """Test de la détermination du type de composant"""
        parser = DiagramParser(self.minimal_drawio)
        
        # Test avec un style de web application
        web_app_type = parser._determine_component_type('rounded=1;whiteSpace=wrap;html=1;', 'Web App')
        self.assertEqual(web_app_type, 'web-application')
        
        # Test avec un style de base de données
        db_type = parser._determine_component_type('shape=cylinder3;whiteSpace=wrap;html=1;', 'Database')
        self.assertEqual(db_type, 'database')

    def test_extract_data_assets(self):
        """Test de l'extraction des assets de données"""
        parser = DiagramParser(self.minimal_drawio)
        
        # Test avec un composant contenant des données utilisateur
        user_data = parser._extract_data_assets({'value': 'User Profile Database'})
        self.assertTrue(any(asset['sensitivity'] == 'confidential' for asset in user_data))
        
        # Test avec un composant contenant des données métier
        business_data = parser._extract_data_assets({'value': 'Order Processing System'})
        self.assertTrue(any(asset['sensitivity'] == 'restricted' for asset in business_data))

    def test_determine_protocol(self):
        """Test de la détermination du protocole"""
        parser = DiagramParser(self.minimal_drawio)
        
        # Test avec des composants API
        api_protocol = parser._determine_protocol(
            '', 
            '', 
            {'type': 'api'}, 
            {'type': 'web-application'}
        )
        self.assertEqual(api_protocol, 'https')
        
        # Test avec des composants base de données
        db_protocol = parser._determine_protocol(
            '', 
            '', 
            {'type': 'database'}, 
            {'type': 'api'}
        )
        self.assertEqual(db_protocol, 'tcp')

    def test_extract_threats(self):
        """Test de l'extraction des menaces"""
        parser = DiagramParser(self.threat_drawio)
        threats = parser._extract_threats(parser._extract_cells())
        
        # Vérifie la présence de la menace SQL Injection
        self.assertTrue(any(threat['name'] == 'SQL Injection' for threat in threats))
        
        # Vérifie le niveau de risque
        sql_injection = next(threat for threat in threats if threat['name'] == 'SQL Injection')
        self.assertIn(sql_injection['risk_level'], ['critical', 'high', 'medium', 'low'])

    def test_to_threagile_format(self):
        """Test de la conversion en format Threagile"""
        parser = DiagramParser(self.minimal_drawio)
        threagile = parser.to_threagile_format()
        
        # Vérifie la structure de base
        self.assertIn('project', threagile)
        self.assertIn('technical_assets', threagile)
        self.assertIn('data_flows', threagile)
        self.assertIn('threats', threagile)
        
        # Vérifie la présence des composants
        self.assertTrue(any(asset['name'] == 'Web App' for asset in threagile['technical_assets']))
        self.assertTrue(any(asset['name'] == 'Database' for asset in threagile['technical_assets']))
        
        # Vérifie la présence des flux
        self.assertTrue(len(threagile['data_flows']) > 0)

    def test_component_attributes(self):
        """Test des attributs des composants"""
        parser = DiagramParser(self.minimal_drawio)
        components = parser._identify_components(parser._extract_cells())
        
        for component in components:
            # Vérifie la présence des attributs requis
            self.assertIn('id', component)
            self.assertIn('name', component)
            self.assertIn('type', component)
            self.assertIn('authentication', component)
            self.assertIn('authorization', component)
            self.assertIn('data_sensitivity', component)
            
            # Vérifie la cohérence des attributs
            if component['type'] == 'web-application':
                self.assertEqual(component['authentication'], 'required')
                self.assertEqual(component['authorization'], 'required')
                self.assertEqual(component['data_sensitivity'], 'internal')

    def test_flow_attributes(self):
        """Test des attributs des flux"""
        parser = DiagramParser(self.minimal_drawio)
        flows = parser._identify_flows(parser._extract_cells())
        
        for flow in flows:
            # Vérifie la présence des attributs requis
            self.assertIn('id', flow)
            self.assertIn('name', flow)
            self.assertIn('source', flow)
            self.assertIn('target', flow)
            self.assertIn('protocol', flow)
            self.assertIn('authentication', flow)
            self.assertIn('authorization', flow)
            self.assertIn('encryption', flow)
            self.assertIn('security_level', flow)
            self.assertIn('data_sensitivity', flow)
            self.assertIn('data_assets', flow)

if __name__ == '__main__':
    unittest.main() 