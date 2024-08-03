library(EpiEstim)
packageVersion("EpiEstim")
exit()

calculate_rt <- function(infection_counts, mean_si, std_si) {
  # 找到末尾的连续零数量
  last_non_zero_index <- max(which(infection_counts != 0))
  last_non_zero_index <- min(last_non_zero_index + 7, length(infection_counts))
  zero_tail_length <- length(infection_counts) - last_non_zero_index

  # 去除末尾的连续零进行估计
  trimmed_counts <- infection_counts[1:last_non_zero_index]

  res <- estimate_R(incid = trimmed_counts,
                    method = "parametric_si",
                    config = make_config(list(mean_si = mean_si,
                                              std_si = std_si)))
  
  rt_values <- res$R$`Mean(R)`

  current_length <- length(rt_values)
  target_length <- length(infection_counts)
  if (current_length < target_length) {
    rt_values <- c(rt_values, rep(0, target_length - current_length))
  }

  return(rt_values[7:length(rt_values)])
}


args <- commandArgs(trailingOnly = TRUE)
mean_si <- as.numeric(args[1])
std_si <- as.numeric(args[2])

# Read infection counts from stdin
infection_counts <- scan("stdin", quiet = TRUE)

# Calculate Rt
rt_values <- calculate_rt(infection_counts, mean_si, std_si)

# Write Rt to stdout
write(rt_values, stdout())


# # 测试参数
# mean_si <- 3.0
# std_si <- 1.5

# # 示例感染计数
# infection_counts <- c(0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 4, 6, 9, 15, 22, 34, 53, 80, 122, 185, 280, 422, 634, 946, 1397, 2035, 2904, 4028, 5381, 6858, 8283, 9459, 10243, 10593, 10547, 10193, 9623, 8921, 8155, 7373, 6608, 5882, 5208, 4590, 4032, 3532, 3086, 2692, 2345, 2040, 1773, 1540, 1336, 1159, 1004, 870, 754, 653, 565, 489, 424, 367, 317, 274, 237, 205, 178, 154, 133, 115, 99, 86, 74, 64, 55, 48, 41, 36, 31, 27, 23, 20, 17, 15, 13, 11, 9, 8, 7, 6, 5, 4, 4, 3, 3, 2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

# # 计算Rt值
# rt_values <- calculate_rt(infection_counts, mean_si, std_si)

# # 输出Rt值
# print(rt_values)

