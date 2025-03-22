from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import random
import os
import sys
import platform
from app.models.config import SurveyLog
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class McDoSurveyBot:
    def __init__(self, headless=False):
        self.setup_driver(headless)
        self.url = "https://survey2.medallia.eu/?hellomcdo"
        
    def setup_driver(self, headless):
        """Setup the Selenium WebDriver"""
        try:
            print("Setting up Chrome WebDriver...")
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-extensions")
            
            # On Windows, use direct initialization which is more reliable
            print("Initializing Chrome WebDriver...")
            self.driver = webdriver.Chrome(options=chrome_options)
            return True  # Retourne True en cas de succès
        except Exception as e:
            print(f"Failed to initialize Chrome: {str(e)}")
            raise Exception(f"Could not initialize Chrome. Make sure Chrome is installed. Error: {str(e)}")
        
    def start_survey(self):
        """Navigate to the survey page and click the start button"""
        try:
            self.driver.get(self.url)
            print(f"Navigating to {self.url}")
            
            # Attendre que la page se charge complètement (réduit de 5s à 2s)
            time.sleep(2)
            print("✅ Page chargée")
            
            # Prendre une capture d'écran pour voir l'état de la page
            self.driver.save_screenshot("before_click.png")
            
            try:
                # Essai 1: Combinaison directe de tous les sélecteurs possibles
                print("Trying combined selectors for start button...")
                start_button_js = self.driver.execute_script("""
                    // Essayer plusieurs sélecteurs en une seule fois
                    var btn = document.querySelector('.start-button, .green-button, button.btn-primary, button.start');
                    
                    if (!btn) {
                        // Si toujours pas trouvé, parcourir tous les boutons
                        var allButtons = document.querySelectorAll('button, a.button');
                        for (var i = 0; i < allButtons.length; i++) {
                            if (allButtons[i].textContent.includes('Commencer')) {
                                btn = allButtons[i];
                                break;
                            }
                        }
                    }
                    
                    if (btn) {
                        btn.click();
                        return true;
                    }
                    return false;
                """)
                
                if start_button_js:
                    print("✅ SUCCÈS: Bouton trouvé et cliqué avec JavaScript")
                
                if not start_button_js:
                    # Essai 2: Sélecteurs directs si JavaScript échoue
                    print("JavaScript failed, trying XPath selector...")
                    element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Commencer l')]"))
                    )
                    self.driver.execute_script("arguments[0].click();", element)
                    print("✅ SUCCÈS: Bouton trouvé et cliqué avec XPath")
            except Exception as e:
                print(f"❌ ERREUR: Button click attempts failed: {str(e)}")
                return False
            
            # Attendre moins longtemps (1s au lieu de 2s)
            time.sleep(1)
            self.driver.save_screenshot("after_click.png")
            
            # Vérifier si nous avons avancé à l'étape suivante
            if "Quel est votre âge" in self.driver.page_source:
                print("✅ SUCCÈS: Successfully moved to age selection page")
                return True
            else:
                print("❌ ERREUR: Failed to navigate to the next page")
                return False
                
        except Exception as e:
            print(f"❌ ERREUR: Error starting survey: {str(e)}")
            self.driver.save_screenshot("error_screenshot.png")
            return False
            
    def select_age_group(self, age_group):
        """Select an age group from the options"""
        try:
            # Réduire les captures d'écran et optimiser la sélection
            self.driver.save_screenshot("age_selection_before.png")
            
            # The age groups from the page (moins de 15 ans supprimé)
            age_options = {
                "15_to_24": "Entre 15 et 24 ans",
                "25_to_34": "Entre 25 et 34 ans",
                "35_to_49": "Entre 35 et 49 ans",
                "50_plus": "50 ans et plus"
            }
            
            # If not specified, choose a random age group
            if not age_group or age_group not in age_options:
                age_group = random.choice(list(age_options.keys()))
            
            age_text = age_options[age_group]
            print(f"Selecting age group: {age_text}")
            
            # Méthode combinée optimisée
            age_selected = self.driver.execute_script(f"""
                var ageText = "{age_text}";
                
                // Chercher tous les labels et inputs associés
                var allLabels = document.querySelectorAll('label');
                for (var i = 0; i < allLabels.length; i++) {{
                    if (allLabels[i].textContent.includes(ageText)) {{
                        allLabels[i].click();
                        return true;
                    }}
                }}
                
                // Si pas trouvé, chercher les boutons radio directement
                var radios = document.querySelectorAll('input[type="radio"]');
                // Ignorer le premier bouton qui est "Moins de 15 ans"
                var index = {list(age_options.keys()).index(age_group) + 1};
                if (radios.length > index) {{
                    radios[index].click();
                    return true;
                }} else if (radios.length > 1) {{
                    // Choisir le deuxième bouton (15-24 ans) par défaut
                    radios[1].click();
                    return true;
                }}
                
                return false;
            """)
            
            if not age_selected:
                # Méthode de secours avec XPath
                element = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, f"//label[contains(text(), '{age_text}')]"))
                )
                self.driver.execute_script("arguments[0].click();", element)
            
            # Cliquer sur Suivant avec JavaScript (optimisé et plus rapide)
            time.sleep(0.5)  # Attente réduite
            next_clicked = self.driver.execute_script("""
                // Trouver et cliquer sur le bouton suivant
                var nextBtn = document.querySelector('.next-button, button[type="submit"]');
                if (nextBtn) {
                    nextBtn.click();
                    return true;
                }
                
                // Essayer avec tous les boutons s'il n'est pas trouvé
                var allButtons = document.querySelectorAll('button');
                for (var i = 0; i < allButtons.length; i++) {
                    if (allButtons[i].textContent.includes('Suivant')) {
                        allButtons[i].click();
                        return true;
                    }
                }
                return false;
            """)
            
            if not next_clicked:
                # Méthode de secours
                next_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Suivant')]"))
                )
                next_button.click()
            
            # Attente réduite après le clic
            time.sleep(0.5)
            
            return age_group
        except Exception as e:
            print(f"Error selecting age group: {str(e)}")
            self.driver.save_screenshot("age_error.png")
            return None
            
    def fill_receipt_information(self, date, hour_time, restaurant_number):
        """Fill in the receipt information form (optimisé)"""
        try:
            print(f"Filling receipt info: date={date}, time={hour_time}, restaurant={restaurant_number}")
            
            # Prendre une capture d'écran pour déboguer
            self.driver.save_screenshot("receipt_form_before.png")
            
            # Tout remplir en un seul script JavaScript (beaucoup plus rapide)
            hour, minute = hour_time.split(':')
            
            # Remplir la date d'abord
            try:
                date_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='JJ/MM/AAAA']"))
                )
                date_field.clear()
                date_field.send_keys(date)
                print(f"✅ Date remplie: {date}")
            except Exception as e:
                print(f"❌ Erreur remplissage date: {str(e)}")
                
                # Essayer avec JavaScript si la méthode standard échoue
                self.driver.execute_script(f"""
                    var dateInput = document.querySelector('input[placeholder="JJ/MM/AAAA"], input[type="date"]');
                    if (dateInput) {{
                        dateInput.value = "{date}";
                        dateInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                """)
            
            # Attente supplémentaire pour s'assurer que la page est complètement chargée
            time.sleep(1)
            
            # Prendre une capture après le remplissage de la date
            self.driver.save_screenshot("after_date_fill.png")
            
            # NOUVELLE APPROCHE: Analyser complètement la page pour tout type de champ pour l'heure/minute
            # Tester si la page contient des champs visibles (recherche très large)
            all_inputs_page = self.driver.execute_script("""
                var inputs = document.querySelectorAll('input');
                return {
                    total: inputs.length,
                    types: Array.from(inputs).map(i => i.type).join(', '),
                    ids: Array.from(inputs).map(i => i.id).join(', '),
                    names: Array.from(inputs).map(i => i.name).join(', ')
                };
            """)
            print(f"Analyse de la page: {all_inputs_page}")
            
            # Approche ciblée: utiliser les noms exacts détectés dans les logs
            try:
                # Trouver les champs d'heure et de minutes par leur nom exact
                hour_field = self.driver.find_element(By.NAME, "spl_rng_q_mc_q_hour")
                minute_field = self.driver.find_element(By.NAME, "spl_rng_q_mc_q_minute")
                
                # Remplir l'heure
                hour_field.clear()
                hour_field.send_keys(hour)
                print(f"✅ Heure remplie: {hour}")
                
                # Remplir les minutes
                minute_field.clear()
                minute_field.send_keys(minute)
                print(f"✅ Minutes remplies: {minute}")
                
                # Vérifier les valeurs
                hour_value = hour_field.get_attribute("value")
                minute_value = minute_field.get_attribute("value")
                print(f"Valeurs après remplissage: heure='{hour_value}', minute='{minute_value}'")
                
                # Si les valeurs ne sont pas définies, essayer avec JavaScript
                if not hour_value or not minute_value:
                    print("Remplissage avec JavaScript pour les valeurs manquantes...")
                    self.driver.execute_script(f"""
                        // Cibler les champs par leur nom exact
                        var hourField = document.getElementsByName('spl_rng_q_mc_q_hour')[0];
                        var minuteField = document.getElementsByName('spl_rng_q_mc_q_minute')[0];
                        
                        // Définir les valeurs
                        if (!hourField.value) {{
                            hourField.value = '{hour}';
                            hourField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            hourField.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                        
                        if (!minuteField.value) {{
                            minuteField.value = '{minute}';
                            minuteField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            minuteField.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                    """)
                
                time_filled = True
            except Exception as e:
                print(f"❌ Erreur lors du remplissage ciblé: {str(e)}")
                time_filled = False
            
            # Remplir le numéro de restaurant
            try:
                restaurant_field = self.driver.find_element(By.XPATH, "//input[@type='text' and @maxlength='4']")
                restaurant_field.clear()
                restaurant_field.send_keys(restaurant_number)
                print(f"✅ Numéro de restaurant rempli: {restaurant_number}")
            except Exception as e:
                print(f"❌ Erreur remplissage restaurant: {str(e)}")
                # Essayer avec JavaScript
                self.driver.execute_script(f"""
                    var restaurantInput = document.querySelector('input[maxlength="4"], input[placeholder*="restaurant"]');
                    if (restaurantInput) {{
                        restaurantInput.value = "{restaurant_number}";
                        restaurantInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                """)
            
            # Capture avant de cliquer sur Suivant
            self.driver.save_screenshot("before_next_click.png")
            
            # Attente plus longue pour stabiliser le formulaire
            time.sleep(2)
            
            # Cliquer sur Suivant
            try:
                next_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Suivant')]"))
                )
                next_button.click()
                print("✅ Bouton Suivant cliqué")
            except Exception as e:
                print(f"❌ ERREUR: clic bouton Suivant: {str(e)}")
                # Essayer avec JavaScript
                self.driver.execute_script("""
                    var nextButton = document.querySelector('button[type="submit"], .next-button');
                    if (nextButton) {
                        nextButton.click();
                    } else {
                        // Chercher tous les boutons avec le texte "Suivant"
                        var allButtons = document.querySelectorAll('button');
                        for (var i = 0; i < allButtons.length; i++) {
                            if (allButtons[i].textContent.includes('Suivant')) {
                                allButtons[i].click();
                                break;
                            }
                        }
                    }
                """)
            
            # Attente réduite
            time.sleep(1)
            
            # Capture après avoir cliqué sur Suivant
            self.driver.save_screenshot("after_next_click.png")
            
            # Vérifier si nous avons avancé à la page suivante (celle des questions du sondage)
            current_url = self.driver.current_url
            page_source = self.driver.page_source
            
            # Si on est toujours sur la même page, vérifier s'il y a des erreurs
            if "Erreur : Champ obligatoire" in page_source:
                print("❌ ERREUR: Certains champs sont toujours marqués comme obligatoires")
                return False
            
            return True
        except Exception as e:
            print(f"❌ ERREUR: Error filling receipt information: {str(e)}")
            self.driver.save_screenshot("receipt_error.png")
            return False
            
    def complete_survey(self, restaurant_number, date, hour_time):
        """Complete the McDonald's survey using the provided information"""
        try:
            print(f"Starting survey completion for restaurant {restaurant_number} on {date} at {hour_time}")
            
            # Initialiser le navigateur et aller à la page
            if not self.setup_driver(False):
                print("❌ ERREUR: Browser setup failed, aborting survey")
                return False
            
            print("✅ SUCCÈS: Navigateur configuré avec succès")
            
            # Démarrer l'enquête
            if not self.start_survey():
                print("❌ ERREUR: Starting survey failed, aborting")
                return False
            
            print("✅ SUCCÈS: Successfully started survey, proceeding to age selection")
            
            # Sélectionner le groupe d'âge (18-24 par défaut)
            selected_age = self.select_age_group(None)
            if not selected_age:
                print("❌ ERREUR: Age group selection failed, aborting")
                return False
            
            print(f"✅ SUCCÈS: Successfully selected age group '{selected_age}', proceeding to receipt information")
            
            # Remplir les informations du ticket
            if not self.fill_receipt_information(date, hour_time, restaurant_number):
                print("❌ ERREUR: Filling receipt information failed, aborting")
                return False
            
            print("✅ SUCCÈS: Successfully filled receipt information, proceeding to survey questions")
            
            # Répondre aux questions de l'enquête
            if not self.answer_survey_questions():
                print("❌ ERREUR: Answering survey questions failed, aborting")
                return False
            
            print("✅ SUCCÈS: Survey completed successfully!")
            
            # Prendre une capture d'écran finale
            self.driver.save_screenshot("survey_completed.png")
            print("✅ Screenshot of completed survey saved as survey_completed.png")
            
            # Ajouter un temps d'attente supplémentaire avant de fermer le navigateur
            final_wait = 3  # Attendre 3 secondes supplémentaires
            print(f"⏱️ Attente finale de {final_wait} secondes avant de fermer le navigateur...")
            time.sleep(final_wait)
            
            return True
        
        except Exception as e:
            print(f"❌ ERREUR: Error completing survey: {str(e)}")
            if hasattr(self, 'driver'):
                self.driver.save_screenshot("survey_error.png")
            return False
        
        finally:
            # S'assurer que le navigateur est fermé
            if hasattr(self, 'driver'):
                try:
                    self.driver.quit()
                    print("✅ SUCCÈS: Browser closed successfully")
                except Exception as e:
                    print(f"❌ ERREUR: Error closing browser: {str(e)}")
    
    def run_survey(self, age_group=None, date=None, hour_time=None, restaurant_number=None):
        """Run the survey with the provided or default information"""
        try:
            # Set default values if not provided
            if not date:
                # Générer une date dans le mois actuel
                today = datetime.now()
                current_month = today.month
                current_year = today.year
                
                # Trouver le nombre de jours dans le mois actuel
                if current_month in [4, 6, 9, 11]:
                    max_days = 30
                elif current_month == 2:
                    # Gestion des années bissextiles
                    if (current_year % 4 == 0 and current_year % 100 != 0) or (current_year % 400 == 0):
                        max_days = 29
                    else:
                        max_days = 28
                else:
                    max_days = 31
                
                # Générer un jour aléatoire entre 1 et aujourd'hui (pour éviter les dates futures)
                max_day = min(max_days, today.day)
                day = random.randint(1, max_day)
                
                # Créer la date dans le mois actuel
                survey_date = datetime(current_year, current_month, day)
                date = survey_date.strftime("%d/%m/%Y")
                print(f"✅ Date générée dans le mois actuel: {date}")

            if not hour_time:
                # Default to a random time between 9am and 9pm
                hour = random.randint(9, 21)
                minute = random.choice([0, 15, 30, 45])
                hour_time = f"{hour:02d}:{minute:02d}"
                print(f"✅ Heure générée: {hour_time}")

            if not restaurant_number:
                # Default to a random 4-digit restaurant number
                restaurant_number = str(random.randint(1000, 9999))
                print(f"✅ Numéro de restaurant généré: {restaurant_number}")

            print(f"=== DÉMARRAGE DU SONDAGE AVEC: Date={date}, Heure={hour_time}, Restaurant={restaurant_number} ===")
            
            # Complete the survey
            survey_result = self.complete_survey(restaurant_number, date, hour_time)
            if not survey_result:
                print("❌ ÉCHEC: Le sondage n'a pas pu être complété")
                return {
                    "status": "error",
                    "message": "Failed to complete survey"
                }

            # Return success result
            print("✅ SUCCÈS FINAL: Sondage complété avec succès!")
            return {
                "status": "success",
                "message": "Survey completed successfully",
                "data": {
                    "date": date,
                    "time": hour_time,
                    "restaurant_number": restaurant_number
                }
            }
        except Exception as e:
            print(f"❌ ERREUR FINALE: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    def close(self):
        """Close the browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def answer_survey_questions(self):
        """Answer survey questions with 'Très satisfait' options"""
        try:
            print("Sélection de l'option 'Très satisfait' pour toutes les questions")
            
            # Enregistrer le temps de début pour contrôler la durée totale
            start_time = time.time()
            
            # Compter combien de fois nous avons cliqué sur "Suivant" avec succès
            next_clicks = 0
            max_pages = 8  # Maximum de pages de questions attendues
            
            while next_clicks < max_pages:
                # Vérifier si nous sommes à la page de confirmation/fin
                if any(text in self.driver.page_source for text in ["Merci", "Thank you", "Confirmation"]):
                    print("✅ SUCCÈS: Reached end of survey")
                    
                    # Attendre sur la page finale (100%)
                    final_wait_time = 15  # Attendre 15 secondes sur la page finale
                    print(f"⏱️ Attente de {final_wait_time} secondes sur la page finale (100%)...")
                    time.sleep(final_wait_time)
                    
                    break
                
                # Vérifier si nous sommes sur la question "Est-ce que votre commande était exacte ?"
                is_order_correct_question = "commande était exacte" in self.driver.page_source or "order correct" in self.driver.page_source.lower()
                
                # Vérifier si nous sommes sur la question "Avez-vous rencontré un problème durant votre visite ?"
                is_problem_question = "rencontré un problème" in self.driver.page_source or "problem during your visit" in self.driver.page_source.lower()
                
                # Vérifier si nous sommes sur la question "Pour quelles raisons dites-vous cela ?"
                is_feedback_question = "Pour quelles raisons dites-vous cela" in self.driver.page_source or "Why do you say that" in self.driver.page_source.lower()
                
                if is_feedback_question:
                    print("Question sur les raisons détectée - Entrée d'un commentaire positif")
                    
                    # Liste de commentaires positifs aléatoires
                    positive_comments = [
                        "Service rapide et personnel très aimable, toujours souriant !",
                        "Nourriture délicieuse et service impeccable, merci !",
                        "Personnel accueillant et restaurant très propre, j'adore venir ici !",
                        "Le service était excellent et très rapide aujourd'hui !",
                        "Je suis toujours bien accueilli dans ce restaurant, c'est pour ça que j'y reviens !",
                        "Ambiance agréable et service très attentionné, bravo à toute l'équipe !",
                        "Super accueil et commande servie très rapidement, parfait !",
                        "Le personnel est toujours de bonne humeur et vraiment serviable !",
                        "Service vraiment au top et personnel très attentif à nos besoins !",
                        "Expérience client parfaite, personnel souriant et efficace !"
                    ]
                    
                    # Sélectionner un commentaire aléatoire - UNIQUEMENT UNE FOIS
                    random_comment = random.choice(positive_comments)
                    
                    # Faire les 2 opérations en un seul script pour éviter les répétitions
                    success = self.driver.execute_script(f"""
                        // 1. D'abord entrer le commentaire une seule fois
                        var commentEntered = false;
                        
                        // Chercher le champ de texte pour le commentaire
                        var textareas = document.querySelectorAll('textarea');
                        var inputs = document.querySelectorAll('input[type="text"]');
                        
                        // Essayer avec les textareas d'abord
                        for (var i = 0; i < textareas.length; i++) {{
                            textareas[i].value = "{random_comment}";
                            textareas[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                            textareas[i].dispatchEvent(new Event('change', {{ bubbles: true }}));
                            commentEntered = true;
                            break; // Sortir après le premier textarea
                        }}
                        
                        // Sinon essayer avec les champs texte
                        if (!commentEntered) {{
                            for (var i = 0; i < inputs.length; i++) {{
                                inputs[i].value = "{random_comment}";
                                inputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                                inputs[i].dispatchEvent(new Event('change', {{ bubbles: true }}));
                                commentEntered = true;
                                break; // Sortir après le premier input
                            }}
                        }}
                        
                        // 2. Ensuite sélectionner l'option "Très satisfait" en une seule fois
                        var radioSelected = false;
                        
                        // Chercher d'abord les boutons radio
                        var radioGroups = {{}};
                        var allRadios = document.querySelectorAll('input[type="radio"]');
                        
                        // Regrouper les boutons radio par nom
                        for (var i = 0; i < allRadios.length; i++) {{
                            var name = allRadios[i].getAttribute('name');
                            if (!name) name = 'group_' + i;
                            if (!radioGroups[name]) radioGroups[name] = [];
                            radioGroups[name].push(allRadios[i]);
                        }}
                        
                        for (var group in radioGroups) {{
                            var radios = radioGroups[group];
                            if (radios.length > 0) {{
                                // Chercher d'abord l'option "Très satisfait" par le texte du label
                                var found = false;
                                for (var j = 0; j < radios.length; j++) {{
                                    var radio = radios[j];
                                    var id = radio.getAttribute('id');
                                    if (id) {{
                                        var label = document.querySelector('label[for="' + id + '"]');
                                        if (label && (
                                            label.textContent.includes('Très satisfait') || 
                                            label.textContent.includes('Very satisfied') ||
                                            label.textContent.includes('5') ||
                                            label.textContent.includes('Excellent')
                                        )) {{
                                            if (!radio.checked) {{ // Vérifier s'il n'est pas déjà coché
                                                radio.click();
                                            }}
                                            found = true;
                                            radioSelected = true;
                                            break;
                                        }}
                                    }}
                                }}
                                
                                // Si on n'a pas trouvé l'option par texte, prendre la première option
                                if (!found) {{
                                    // La première option est généralement "Très satisfait"
                                    if (!radios[0].checked) {{ // Vérifier s'il n'est pas déjà coché
                                        radios[0].click();
                                    }}
                                    radioSelected = true;
                                }}
                                
                                break; // Important: sortir après avoir traité un groupe
                            }}
                        }}
                        
                        return {{
                            commentEntered: commentEntered,
                            radioSelected: radioSelected
                        }};
                    """)
                    
                    if success.get('commentEntered'):
                        print(f"✅ SUCCÈS: Commentaire positif entré: '{random_comment}'")
                    else:
                        print("❌ ERREUR: Impossible d'entrer un commentaire positif")
                        # Méthode de secours avec Selenium - une seule tentative
                        try:
                            textarea = self.driver.find_element(By.TAG_NAME, "textarea")
                            textarea.clear()
                            textarea.send_keys(random_comment)
                            print(f"✅ SUCCÈS: Commentaire positif entré avec méthode de secours: '{random_comment}'")
                        except Exception as e:
                            print(f"❌ ERREUR: Secours textarea a échoué: {str(e)}")
                            try:
                                text_input = self.driver.find_element(By.XPATH, "//input[@type='text']")
                                text_input.clear()
                                text_input.send_keys(random_comment)
                                print(f"✅ SUCCÈS: Commentaire positif entré avec méthode de secours input: '{random_comment}'")
                            except Exception as e:
                                print(f"❌ ERREUR: Secours input a échoué: {str(e)}")
                    
                    if success.get('radioSelected'):
                        print("✅ SUCCÈS: Option 'Très satisfait' sélectionnée sur la page de commentaire")
                    else:
                        print("Note: Aucune option 'Très satisfait' n'a été trouvée sur cette page")
                    
                    # Cliquer directement sur "Suivant"
                    time.sleep(0.5)
                    try:
                        next_button = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Suivant')]"))
                        )
                        next_button.click()
                        print("✅ SUCCÈS: Bouton Suivant cliqué sur la page de commentaire")
                    except Exception as e:
                        print(f"❌ ERREUR: Impossible de cliquer sur Suivant: {str(e)}")
                        # Essayer avec JavaScript
                        self.driver.execute_script("""
                            var nextButton = document.querySelector('button[type="submit"], .next-button');
                            if (nextButton) {
                                nextButton.click();
                            } else {
                                // Chercher tous les boutons avec le texte "Suivant"
                                var allButtons = document.querySelectorAll('button');
                                for (var i = 0; i < allButtons.length; i++) {
                                    if (allButtons[i].textContent.includes('Suivant')) {
                                        allButtons[i].click();
                                        break;
                                    }
                                }
                            }
                        """)
                        print("✅ SUCCÈS: Tentative de clic sur Suivant via JavaScript")
                    
                    # Attendre que la page change
                    time.sleep(1)
                    next_clicks += 1
                    print(f"✅ Page de commentaire {next_clicks} complétée")
                    
                    # Attendre 10 secondes sur cette étape
                    print(f"⏱️ Attente de 10 secondes sur l'étape {next_clicks}...")
                    time.sleep(10)
                    
                    # Passer à l'itération suivante de la boucle
                    continue
                elif is_problem_question:
                    print("Question sur les problèmes rencontrés détectée - Sélection de 'Non'")
                    # Sélectionner "Non" avec JavaScript
                    problem_selected = self.driver.execute_script("""
                        // Chercher tous les boutons radio
                        var allRadios = document.querySelectorAll('input[type="radio"]');
                        for (var i = 0; i < allRadios.length; i++) {
                            var radio = allRadios[i];
                            var id = radio.getAttribute('id');
                            if (id) {
                                var label = document.querySelector('label[for="' + id + '"]');
                                if (label && (
                                    label.textContent.includes('Non') || 
                                    label.textContent.includes('No')
                                )) {
                                    radio.click();
                                    return true;
                                }
                            }
                        }
                        
                        // Si pas trouvé par label, chercher par valeur
                        for (var i = 0; i < allRadios.length; i++) {
                            var value = allRadios[i].getAttribute('value');
                            if (value && (value.includes('non') || value.includes('no'))) {
                                allRadios[i].click();
                                return true;
                            }
                        }
                        
                        // Si toujours pas trouvé, prendre le deuxième (généralement Non/No)
                        if (allRadios.length > 1) {
                            allRadios[1].click();
                            return true;
                        }
                        
                        return false;
                    """)
                    
                    if problem_selected:
                        print("✅ SUCCÈS: Option 'Non' sélectionnée pour la question sur les problèmes rencontrés")
                    else:
                        print("❌ ERREUR: Impossible de sélectionner 'Non' pour la question sur les problèmes rencontrés")
                    
                    # Cliquer directement sur "Suivant"
                    time.sleep(0.5)
                    try:
                        next_button = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Suivant')]"))
                        )
                        next_button.click()
                        print("✅ SUCCÈS: Bouton Suivant cliqué sur la page de problèmes rencontrés")
                    except Exception as e:
                        print(f"❌ ERREUR: Impossible de cliquer sur Suivant: {str(e)}")
                        # Essayer avec JavaScript
                        self.driver.execute_script("""
                            var nextButton = document.querySelector('button[type="submit"], .next-button');
                            if (nextButton) {
                                nextButton.click();
                            } else {
                                // Chercher tous les boutons avec le texte "Suivant"
                                var allButtons = document.querySelectorAll('button');
                                for (var i = 0; i < allButtons.length; i++) {
                                    if (allButtons[i].textContent.includes('Suivant')) {
                                        allButtons[i].click();
                                        break;
                                    }
                                }
                            }
                        """)
                        print("✅ SUCCÈS: Tentative de clic sur Suivant via JavaScript")
                    
                    # Attendre que la page change
                    time.sleep(1)
                    next_clicks += 1
                    print(f"✅ Page de problèmes rencontrés {next_clicks} complétée")
                    
                    # Attendre 10 secondes sur cette étape
                    print(f"⏱️ Attente de 10 secondes sur l'étape {next_clicks}...")
                    time.sleep(10)
                    
                    # Passer à l'itération suivante de la boucle
                    continue
                elif is_order_correct_question:
                    print("Question sur l'exactitude de la commande détectée - Sélection de 'Oui'")
                    # Sélectionner "Oui" avec JavaScript
                    order_correct_selected = self.driver.execute_script("""
                        // Chercher tous les boutons radio
                        var allRadios = document.querySelectorAll('input[type="radio"]');
                        for (var i = 0; i < allRadios.length; i++) {
                            var radio = allRadios[i];
                            var id = radio.getAttribute('id');
                            if (id) {
                                var label = document.querySelector('label[for="' + id + '"]');
                                if (label && (
                                    label.textContent.includes('Oui') || 
                                    label.textContent.includes('Yes')
                                )) {
                                    radio.click();
                                    return true;
                                }
                            }
                        }
                        
                        // Si pas trouvé par label, chercher par valeur
                        for (var i = 0; i < allRadios.length; i++) {
                            var value = allRadios[i].getAttribute('value');
                            if (value && (value.includes('oui') || value.includes('yes'))) {
                                allRadios[i].click();
                                return true;
                            }
                        }
                        
                        // Si toujours pas trouvé, prendre le premier (généralement Oui/Yes)
                        if (allRadios.length > 0) {
                            allRadios[0].click();
                            return true;
                        }
                        
                        return false;
                    """)
                    
                    if order_correct_selected:
                        print("✅ SUCCÈS: Option 'Oui' sélectionnée pour la question sur l'exactitude de la commande")
                    else:
                        print("❌ ERREUR: Impossible de sélectionner 'Oui' pour la question sur l'exactitude de la commande")
                    
                    # Cliquer directement sur "Suivant"
                    time.sleep(0.5)
                    try:
                        next_button = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Suivant')]"))
                        )
                        next_button.click()
                        print("✅ SUCCÈS: Bouton Suivant cliqué sur la page d'exactitude de commande")
                    except Exception as e:
                        print(f"❌ ERREUR: Impossible de cliquer sur Suivant: {str(e)}")
                        # Essayer avec JavaScript
                        self.driver.execute_script("""
                            var nextButton = document.querySelector('button[type="submit"], .next-button');
                            if (nextButton) {
                                nextButton.click();
                            } else {
                                // Chercher tous les boutons avec le texte "Suivant"
                                var allButtons = document.querySelectorAll('button');
                                for (var i = 0; i < allButtons.length; i++) {
                                    if (allButtons[i].textContent.includes('Suivant')) {
                                        allButtons[i].click();
                                        break;
                                    }
                                }
                            }
                        """)
                        print("✅ SUCCÈS: Tentative de clic sur Suivant via JavaScript")
                    
                    # Attendre que la page change
                    time.sleep(1)
                    next_clicks += 1
                    print(f"✅ Page d'exactitude de commande {next_clicks} complétée")
                    
                    # Attendre 10 secondes sur cette étape
                    print(f"⏱️ Attente de 10 secondes sur l'étape {next_clicks}...")
                    time.sleep(10)
                    
                    # Passer à l'itération suivante de la boucle
                    continue
                else:
                    # Méthode rapide: sélectionner les options "Très satisfait" et cliquer sur suivant en JavaScript
                    selections_made = self.driver.execute_script("""
                        // Sélectionner l'option "Très satisfait" pour tous les groupes
                        var radioGroups = {};
                        var success = false;
                        
                        // Collecter tous les boutons radio par nom
                        var allRadios = document.querySelectorAll('input[type="radio"]');
                        for (var i = 0; i < allRadios.length; i++) {
                            var name = allRadios[i].getAttribute('name');
                            if (!name) name = 'group_' + i;
                            if (!radioGroups[name]) radioGroups[name] = [];
                            radioGroups[name].push(allRadios[i]);
                        }
                        
                        // Pour chaque groupe, sélectionner la première option (généralement "Très satisfait")
                        // ou la dernière, selon la conception du sondage
                        for (var group in radioGroups) {
                            var radios = radioGroups[group];
                            if (radios.length > 0) {
                                // Chercher d'abord l'option "Très satisfait" par le texte du label
                                var found = false;
                                for (var j = 0; j < radios.length; j++) {
                                    var radio = radios[j];
                                    var id = radio.getAttribute('id');
                                    if (id) {
                                        var label = document.querySelector('label[for="' + id + '"]');
                                        if (label && (
                                            label.textContent.includes('Très satisfait') || 
                                            label.textContent.includes('Very satisfied') ||
                                            label.textContent.includes('5') ||
                                            label.textContent.includes('Excellent')
                                        )) {
                                            radio.click();
                                            found = true;
                                            success = true;
                                            break;
                                        }
                                    }
                                }
                                
                                // Si on n'a pas trouvé l'option par texte, prendre la première option
                                // qui correspond généralement à la meilleure note
                                if (!found) {
                                    // La première option est généralement "Très satisfait"
                                    radios[0].click();
                                    success = true;
                                }
                            }
                        }
                        
                        // Si aucun bouton radio n'est trouvé, chercher d'autres éléments cliquables
                        if (!success) {
                            // Chercher d'abord par le texte
                            var allOptions = document.querySelectorAll('.option, .choice, .answer, li[role="option"]');
                            var foundOption = false;
                            
                            for (var i = 0; i < allOptions.length; i++) {
                                if (
                                    allOptions[i].textContent.includes('Très satisfait') || 
                                    allOptions[i].textContent.includes('Very satisfied') ||
                                    allOptions[i].textContent.includes('5') ||
                                    allOptions[i].textContent.includes('Excellent')
                                ) {
                                    allOptions[i].click();
                                    foundOption = true;
                                    success = true;
                                    break;
                                }
                            }
                            
                            // Si on n'a pas trouvé par texte, prendre la première option de chaque groupe
                            if (!foundOption && allOptions.length > 0) {
                                // Regrouper les options
                                var groups = {};
                                for (var i = 0; i < allOptions.length; i++) {
                                    var parent = allOptions[i].parentNode;
                                    var groupId = parent.tagName + '_' + i;
                                    if (!groups[groupId]) groups[groupId] = [];
                                    groups[groupId].push(allOptions[i]);
                                }
                                
                                // Cliquer sur la première option de chaque groupe
                                for (var group in groups) {
                                    if (groups[group].length > 0) {
                                        groups[group][0].click();
                                        success = true;
                                    }
                                }
                            }
                        }
                        
                        // Cliquer sur le bouton Suivant
                        setTimeout(function() {
                            var nextButton = document.querySelector('button[type="submit"], .next-button');
                            if (nextButton) {
                                nextButton.click();
                            }
                        }, 100);
                        
                        return success;
                    """)
                    
                    if selections_made:
                        print(f"✅ SUCCÈS: Options 'Très satisfait' sélectionnées sur la page {next_clicks + 1}")
                    
                    if not selections_made and not is_order_correct_question and not is_problem_question and not is_feedback_question:
                        # Méthode de secours avec les sélecteurs standard
                        try:
                            # Recherche des boutons radio et sélection de la première option (généralement "Très satisfait")
                            all_radios = self.driver.find_elements(By.XPATH, "//input[@type='radio']")
                            radio_by_name = {}
                            for radio in all_radios:
                                name = radio.get_attribute("name") or "unnamed"
                                if name not in radio_by_name:
                                    radio_by_name[name] = []
                                radio_by_name[name].append(radio)
                            
                            for name, radios in radio_by_name.items():
                                if radios:
                                    # Cliquer sur le premier bouton radio de chaque groupe (généralement "Très satisfait")
                                    self.driver.execute_script("arguments[0].click();", radios[0])
                            print(f"✅ SUCCÈS: Options 'Très satisfait' sélectionnées avec méthode de secours sur la page {next_clicks + 1}")
                        except Exception as e:
                            print(f"❌ ERREUR: Backup selection method failed: {str(e)}")
                    
                    # Attente courte (0.5s au lieu de 1s)
                    time.sleep(0.5)
                    
                    # Cliquer sur Suivant (si le JavaScript n'a pas fonctionné)
                    try:
                        next_button = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Suivant')]"))
                        )
                        next_button.click()
                        print(f"✅ SUCCÈS: Bouton Suivant cliqué sur la page {next_clicks + 1}")
                    except:
                        pass  # Ignorer les erreurs car le JavaScript a peut-être déjà cliqué
                    
                    next_clicks += 1
                    time.sleep(0.5)  # Attente réduite
                    print(f"✅ Page {next_clicks} complétée")
                
                # Attendre 10 secondes sur cette étape
                print(f"⏱️ Attente de 10 secondes sur l'étape {next_clicks}...")
                time.sleep(10)
            
            # Supprimer la temporisation globale à la fin et la remplacer par un simple calcul du temps écoulé
            elapsed_time = time.time() - start_time
            print(f"⏱️ Temps total passé sur le sondage: {elapsed_time:.2f} secondes")
            print("✅ SUCCÈS: Toutes les questions du sondage ont été répondues avec 'Très satisfait'")
            return True
        except Exception as e:
            print(f"❌ ERREUR: Error in selecting 'Très satisfait' options: {str(e)}")
            return False 

    def run_bulk_surveys(self, count=3, interval_minutes=5, age_group=None, date=None, hour_time=None, restaurant_number="0321"):
        """
        Exécute plusieurs sondages en série avec un intervalle de temps configurable entre chaque exécution
        
        Args:
            count (int): Nombre de sondages à exécuter
            interval_minutes (int): Intervalle en minutes entre chaque sondage
            age_group (str, optional): Groupe d'âge à sélectionner
            date (str, optional): Date au format JJ/MM/AAAA
            hour_time (str, optional): Heure au format HH:MM
            restaurant_number (str, optional): Numéro du restaurant (défaut: "0321")
            
        Returns:
            dict: Résultat de l'exécution des sondages
        """
        try:
            results = []
            start_time = datetime.now()
            
            print(f"=== DÉMARRAGE DE L'EXÉCUTION EN SÉRIE DE {count} SONDAGES ===")
            print(f"=== INTERVALLE ENTRE SONDAGES: {interval_minutes} minutes ===")
            print(f"=== NUMÉRO DE RESTAURANT UTILISÉ: {restaurant_number} ===")
            
            for i in range(count):
                print(f"\n=== SONDAGE {i+1}/{count} ===")
                
                # Gérer le premier sondage ou calculer le temps d'attente pour les suivants
                if i > 0:
                    # Calculer le temps à attendre avant le prochain sondage
                    wait_seconds = interval_minutes * 60
                    print(f"⏱️ Attente de {interval_minutes} minutes avant le prochain sondage...")
                    
                    # Afficher un compte à rebours pour visualiser l'attente
                    for remaining in range(wait_seconds, 0, -30):
                        minutes_left = remaining // 60
                        seconds_left = remaining % 60
                        print(f"⏱️ Temps restant: {minutes_left}m {seconds_left}s", end="\r")
                        time.sleep(30)
                    print("\n")
                
                # Générer des informations aléatoires pour chaque sondage si non spécifiées
                current_date = date
                current_time = hour_time
                current_restaurant = restaurant_number  # Utiliser le numéro de restaurant fourni
                
                if not current_date:
                    # Date aléatoire dans la semaine passée
                    today = datetime.now()
                    days_ago = random.randint(1, 7)
                    survey_date = today - timedelta(days=days_ago)
                    current_date = survey_date.strftime("%d/%m/%Y")
                
                if not current_time:
                    # Heure aléatoire entre 9h et 21h
                    hour = random.randint(9, 21)
                    minute = random.choice([0, 15, 30, 45])
                    current_time = f"{hour:02d}:{minute:02d}"
                
                # Exécuter le sondage
                start_survey_time = datetime.now()
                result = self.run_survey(age_group, current_date, current_time, current_restaurant)
                end_survey_time = datetime.now()
                
                # Ajouter le résultat avec des informations sur le temps d'exécution
                result['execution_time'] = str(end_survey_time - start_survey_time)
                results.append(result)
                
                print(f"=== FIN DU SONDAGE {i+1}/{count} ===\n")
            
            # Calculer les statistiques
            end_time = datetime.now()
            total_time = end_time - start_time
            success_count = sum(1 for r in results if r['status'] == 'success')
            
            print(f"\n=== RÉSUMÉ DE L'EXÉCUTION EN SÉRIE ===")
            print(f"Sondages réussis: {success_count}/{count} ({(success_count/count)*100:.1f}%)")
            print(f"Temps total: {total_time}")
            print(f"=== FIN DE L'EXÉCUTION EN SÉRIE ===")
            
            return {
                "status": "success" if success_count == count else "partial_success" if success_count > 0 else "error",
                "total_surveys": count,
                "successful_surveys": success_count,
                "failed_surveys": count - success_count,
                "total_execution_time": str(total_time),
                "results": results
            }
        
        except Exception as e:
            print(f"❌ ERREUR FATALE dans l'exécution en série: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "total_surveys": count,
                "successful_surveys": len([r for r in results if r['status'] == 'success']) if 'results' in locals() else 0
            } 