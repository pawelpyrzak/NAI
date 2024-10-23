package com.example.multimodule;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;


@SpringBootTest
public class DemoApplicationTest {
	private WebDriver driver;

	@BeforeEach
	public void setUp() {
		// Upewnij się, że masz zainstalowanego WebDrivera do Chrome'a i że ścieżka do chromedriver jest poprawna
		System.setProperty("webdriver.chrome.driver", "C:/Users/matey/Desktop/chromedriver-win64/chromedriver.exe");
		driver = new ChromeDriver();
	}

	@Test
	public void testLogin() {
		// Przejdź na stronę logowania
		driver.get("http://localhost:8080/login");

		// Znajdź pola loginu i hasła
		WebElement usernameField = driver.findElement(By.name("username"));
		WebElement passwordField = driver.findElement(By.name("password"));
		WebElement loginButton = driver.findElement(By.cssSelector("button[type='submit']"));

		// Wprowadź dane logowania
		usernameField.sendKeys("yourUsername");
		passwordField.sendKeys("yourPassword");

		// Kliknij przycisk logowania
		loginButton.click();

		// Sprawdź, czy po zalogowaniu został przekierowany na odpowiednią stronę
		Assertions.assertEquals("http://localhost:8080/home", driver.getCurrentUrl());
	}

	@AfterEach
	public void tearDown() {
		if (driver != null) {
			driver.quit(); // Zamknij przeglądarkę po teście
		}
	}

}
