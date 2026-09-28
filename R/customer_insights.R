suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
  library(readr)
  library(scales)
  library(tidyr)
})

dir.create("figures", showWarnings = FALSE)
customer_360 <- read_csv("outputs/customer_360.csv", show_col_types = FALSE)

stopifnot(nrow(customer_360) == 4085)
stopifnot(n_distinct(customer_360$CustomerID) == 4085)

ownership <- customer_360 %>%
  summarise(
    Motor = sum(HasMotor),
    Health = sum(HasHealth),
    Travel = sum(HasTravel)
  ) %>%
  pivot_longer(everything(), names_to = "Product", values_to = "Customers")

channel <- customer_360 %>%
  count(AgeGroup, ComChannel) %>%
  group_by(AgeGroup) %>%
  mutate(Share = n / sum(n)) %>%
  ungroup()

overview_plot <- ggplot(ownership, aes(Product, Customers, fill = Product)) +
  geom_col(width = 0.65, show.legend = FALSE) +
  geom_text(aes(label = comma(Customers)), vjust = -0.4, size = 4) +
  scale_fill_manual(values = c(Motor = "#2563eb", Health = "#7c3aed", Travel = "#0f766e")) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.12))) +
  labs(title = "Synthetic Customer 360: policy ownership", x = NULL, y = "Customers") +
  theme_minimal(base_size = 12)
ggsave("figures/customer_360_overview.png", overview_plot, width = 9, height = 5.2, dpi = 180)

channel_plot <- ggplot(channel, aes(AgeGroup, Share, fill = ComChannel)) +
  geom_col() +
  scale_y_continuous(labels = percent_format(accuracy = 1)) +
  scale_fill_manual(values = c(Email = "#2563eb", Phone = "#7c3aed", SMS = "#f59e0b")) +
  labs(title = "Synthetic contact preference by age group", x = "Age group", y = "Share", fill = NULL) +
  theme_minimal(base_size = 12) +
  theme(legend.position = "bottom")
ggsave("figures/channel_by_age.png", channel_plot, width = 9, height = 5.2, dpi = 180)

write_csv(ownership, "outputs/product_ownership.csv")
message("R CUSTOMER INSIGHTS COMPLETED")

